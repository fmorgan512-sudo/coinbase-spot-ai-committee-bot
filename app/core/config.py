from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
      db_path: str = os.getenv("DB_PATH", "/data/bot.sqlite3")

    dry_run: bool = os.getenv("DRY_RUN", "true").lower() == "true"

    coinbase_api_key_name: str = os.getenv("COINBASE_API_KEY_NAME", "")
    coinbase_api_private_key_pem: str = os.getenv("COINBASE_API_PRIVATE_KEY_PEM", "")

    quote_currency: str = os.getenv("QUOTE_CURRENCY", "USD")

    poll_seconds: int = int(os.getenv("POLL_SECONDS", "30"))
    ai_min_seconds_between: int = int(os.getenv("AI_MIN_SECONDS_BETWEEN", "1800"))
    pnl_delta_trigger_pct: float = float(os.getenv("PNL_DELTA_TRIGGER_PCT", "0.5"))
    volatility_trigger_pct: float = float(os.getenv("VOLATILITY_TRIGGER_PCT", "1.0"))

    max_daily_loss_pct: float = float(os.getenv("MAX_DAILY_LOSS_PCT", "2.0"))
    max_position_pct: float = float(os.getenv("MAX_POSITION_PCT", "10.0"))
    max_trades_per_hour: int = int(os.getenv("MAX_TRADES_PER_HOUR", "6"))

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")

settings = Settings()
