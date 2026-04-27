from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JARVIS_")

    # Gateway
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    api_key: str = ""

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: int = 120

    # OpenAI
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index: str = "jarvis-memory"

    # Google OAuth2
    google_client_id: str = ""
    google_client_secret: str = ""

    # Notifications
    discord_webhook_url: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    whatsapp_from: str = "whatsapp:+14155238886"
    whatsapp_to: str = ""

    # Database
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'db' / 'jarvis.db'}"

    # Paths
    tokens_dir: Path = BASE_DIR / "data" / "tokens"

    def load_models_config(self) -> dict:
        models_path = BASE_DIR / "config" / "models.yaml"
        with open(models_path) as f:
            return yaml.safe_load(f)


settings = Settings()
