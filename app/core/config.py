from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


def _get_stored_keys() -> dict:
          """Try to load keys from encrypted storage if available."""
          try:
                        from .key_store import load_keys, keys_exist
                        # For worker process, we need the unlock password from env
                        unlock_pwd = os.getenv("KEY_UNLOCK_PASSWORD", "")
                        if keys_exist() and unlock_pwd:
                                          loaded = load_keys(unlock_pwd)
                                          if loaded:
                                                                return loaded
          except Exception:
                        pass
                    return {}


class Settings(BaseModel):
          db_path: str = os.getenv("DB_PATH", "/data/bot.sqlite3")
    dry_run: bool = os.getenv("DRY_RUN", "true").lower() == "true"

    # Try stored keys first, fall back to env vars
    _stored: dict = {}

    @property
    def coinbase_api_key_name(self) -> str:
                  stored = _get_stored_keys()
                  return stored.get("coinbase_api_key_name") or os.getenv("COINBASE_API_KEY_NAME", "")

    @property
    def coinbase_api_private_key_pem(self) -> str:
                  stored = _get_stored_keys()
                  return stored.get("coinbase_api_private_key_pem") or os.getenv("COINBASE_API_PRIVATE_KEY_PEM", "")

    quote_currency: str = os.getenv("QUOTE_CURRENCY", "USD")
    poll_seconds: int = int(os.getenv("POLL_SECONDS", "30"))
    ai_min_seconds_between: int = int(os.getenv("AI_MIN_SECONDS_BETWEEN", "1800"))
    pnl_delta_trigger_pct: float = float(os.getenv("PNL_DELTA_TRIGGER_PCT", "0.5"))
    volatility_trigger_pct: float = float(os.getenv("VOLATILITY_TRIGGER_PCT", "1.0"))
    max_daily_loss_pct: float = float(os.getenv("MAX_DAILY_LOSS_PCT", "2.0"))
    max_position_pct: float = float(os.getenv("MAX_POSITION_PCT", "10.0"))
    max_trades_per_hour: int = int(os.getenv("MAX_TRADES_PER_HOUR", "6"))

    @property
    def openai_api_key(self) -> str:
                  stored = _get_stored_keys()
                  return stored.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")

    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def anthropic_api_key(self) -> str:
                  stored = _get_stored_keys()
                  return stored.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY", "")

    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")


settings = Settings()
