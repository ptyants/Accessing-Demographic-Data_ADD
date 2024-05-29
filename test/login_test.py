from flask import Flask, flash, redirect, url_for, render_template, session, abort, request
# from authlib.integrations.flask_client import OAuth
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import requests
import os
import json
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)
app.secret_key = "Key-chốnghacker-123."
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_ID = "1028993107715-nkl0etge0ks4i3r5mtjmkr6bnbclrg46.apps.googleusercontent.com"

# Lấy đường dẫn tới thư mục chứa tệp mã nguồn Python
current_dir = os.path.dirname(__file__)

# Đường dẫn tới tệp client_secret.json
client_secrets_file = os.path.join(current_dir, 'client_secret.json')

print("Client secrets file path:", client_secrets_file)


flow =Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
    )



def login_is_required(f):
    def warpper(*args, **kwargs):
        if 'google_id' not in session:
            return abort(401)
        else:
            return f()
    return warpper

@app.route('/')
def home():
    return "<h1>Xin chào</h1></br><a href='/login'>Login</a>"

@app.route('/login')
def login():
    authorize_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorize_url)

@app.route('/authorize')
def authorize():
    pass

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protect")


@app.route('/protect')
@login_is_required
def protect():
    print(session.get)
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"

@app.route('/logout')
def logout():
    session.clear()
    print(session.get)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

