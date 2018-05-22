#!/usr/bin/env python3
import json
import flask
import requests
import os

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import logging
import sys
log = logging.getLogger('oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "settings/client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['email', 'profile']

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = os.environ['OAUTH2_PROXY_COOKIE_SECRET']
#b'U\x10\x0e\xb9\x7f\x90\xbd\x83\xda\xfd\xba\x7f\xbf\x90/J\xe9\x96\xe4P8\x128\xf8'

CONFIG = {}

try:
    with open('settings/config.json') as config_file:
        CONFIG = json.load(config_file)
except IOError:
    print("No configuration found.  Exiting.")
    raise

NAME = CONFIG.get('domain_name')
UPSTREAM = CONFIG.get('upstream')
SSL_VERIFY = CONFIG.get('ssl_verify', True)
PASS_HOST_HEADER = CONFIG.get('pass_host_header', True)

@app.route('/')
def proxy():
    """Proxy method, adapted from code by @marciogarcianubeliu"""
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    request_headers = flask.request.headers
    if not PASS_HOST_HEADER:
        request_headers.pop('Host', None)
    request_headers['Authorization'] = f'Bearer {credentials.id_token}'

    try: 
        response = requests.request(
            method=flask.request.method,
            url=UPSTREAM,
            headers=request_headers,
            data=flask.request.get_data(),
            cookies=flask.request.cookies,
            allow_redirects=False,
            verify=SSL_VERIFY
        )

        log.debug(f'Proxied "{UPSTREAM}" with response: {response.status_code}')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = flask.Response(response.content, response.status_code, headers)
        return response

    except Exception as exception:
        log.error(exception)
        return 'Error'

@app.route("/authorize")
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    #response = flask.redirect(REDIRECT_URL, code=int(CODE))
    #response.headers = {'Authorization': f'Bearer {flow.credentials.token}'}

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('entry'))

@app.route("/ping")
def ping():
    return '{"status": "ok"}'

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

if __name__ == "__main__":
    app.run()
