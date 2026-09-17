import os

from flask import Flask, redirect, request, session, Response
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


def make_flow(state=None):
    client_config = {
        "web": {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                os.environ["REDIRECT_URI"]
            ],
        }
    }

    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        state=state,
    )


@app.route("/")
def authorize():
    flow = make_flow()
    flow.redirect_uri = os.environ["REDIRECT_URI"]

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    session["state"] = state
    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback():
    state = session["state"]

    flow = make_flow(state=state)
    flow.redirect_uri = os.environ["REDIRECT_URI"]

    flow.fetch_token(
        authorization_response=request.url
    )

    return Response(
        flow.credentials.to_json(),
        mimetype="application/json",
        headers={
            "Content-Disposition":
                "attachment; filename=gmail_token.json"
        },
    )
