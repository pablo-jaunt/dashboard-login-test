import json
from flask import Flask,redirect,request

app = Flask(__name__)

CONFIG = {}

try:
    with open('settings/config.json') as config_file:
        CONFIG = json.load(config_file)
except IOError:
    print("No CONFIGuration found.  Exiting.")
    raise

NAME = CONFIG.get('domain_name')
OIDC_URL = CONFIG.get('oidc_url')
REDIRECT_URL = CONFIG.get('redirect_url')
CODE = CONFIG.get('response_code', 302)

@app.route("/")
def login():
    return redirect(OIDC_URL, code=int(CODE))

@app.route("/oidc")
def oidc_callback():
    print(request.__dict__)
    #response = redirect(REDIRECT_URL, code=int(CODE))
    #response.headers = {'Authorization': f'Bearer {token}'}

if __name__ == "__main__":
    app.run()
