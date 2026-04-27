import json
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


class GoogleAuth:
    def __init__(self, client_id: str, client_secret: str, tokens_dir: Path):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tokens_dir = tokens_dir
        self.tokens_dir.mkdir(parents=True, exist_ok=True)
        self._token_path = self.tokens_dir / "google.json"

    def _get_client_config(self) -> dict:
        return {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8000/auth/google/callback"],
            }
        }

    def create_auth_flow(self, redirect_uri: str) -> Flow:
        flow = Flow.from_client_config(
            self._get_client_config(),
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )
        return flow

    def get_auth_url(self, redirect_uri: str) -> str:
        flow = self.create_auth_flow(redirect_uri)
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    def exchange_code(self, code: str, redirect_uri: str) -> Credentials:
        flow = self.create_auth_flow(redirect_uri)
        flow.fetch_token(code=code)
        creds = flow.credentials
        self._save_credentials(creds)
        return creds

    def get_credentials(self) -> Credentials | None:
        if not self._token_path.exists():
            return None

        creds = Credentials.from_authorized_user_file(str(self._token_path), SCOPES)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self._save_credentials(creds)

        if not creds.valid:
            return None

        return creds

    def _save_credentials(self, creds: Credentials) -> None:
        self._token_path.write_text(creds.to_json())

    def is_authenticated(self) -> bool:
        return self.get_credentials() is not None
