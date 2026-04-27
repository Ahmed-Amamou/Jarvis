from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from config.settings import settings
from src.jarvis.google.auth import GoogleAuth

router = APIRouter(prefix="/auth")

_google_auth = GoogleAuth(
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    tokens_dir=settings.tokens_dir,
)


@router.get("/google")
async def google_login(request: Request):
    redirect_uri = str(request.url_for("google_callback"))
    auth_url = _google_auth.get_auth_url(redirect_uri)
    return RedirectResponse(auth_url)


@router.get("/google/callback")
async def google_callback(request: Request, code: str):
    redirect_uri = str(request.url_for("google_callback"))
    _google_auth.exchange_code(code, redirect_uri)
    return {"status": "authenticated", "message": "Google account linked successfully."}


@router.get("/status")
async def auth_status():
    return {
        "google_authenticated": _google_auth.is_authenticated(),
    }
