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
SCOPES = ['https://www.googleapis.com/auth/admin.directory.group.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

app = flask.Flask(__name__)

CONFIG = {}

try:
    with open('settings/config.json') as config_file:
        CONFIG = json.load(config_file)
except IOError:
    print("No configuration found.  Exiting.")
    raise

NAME = CONFIG.get('domain_name')
OIDC_URL = CONFIG.get('oidc_url')
REDIRECT_URL = CONFIG.get('redirect_url')
CODE = CONFIG.get('response_code', 302)

@app.route("/")
def login():
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
    return flask.redirect(authorization_url, code=int(CODE))

@app.route("/oauth2callback")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    #authorization_response = flask.request.url
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    response = flask.redirect(REDIRECT_URL, code=int(CODE))
    response.headers = {'Authorization': f'Bearer {flow.credentials.token}'}

    return response

if __name__ == "__main__":
    app.run()
