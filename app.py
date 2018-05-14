import json
import flask
import google_auth_oauthlib

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
    return flask.redirect(OIDC_URL, code=int(CODE))

@app.route("/oidc")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'settings/client_secret.json',
        scopes=['https://www.googleapis.com/auth/admin.directory.group.readonly'],
        state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    response = flask.redirect(REDIRECT_URL, code=int(CODE))
    response.headers = {'Authorization': f'Bearer {flow.credentials.token}'}

    return response

if __name__ == "__main__":
    app.run()
