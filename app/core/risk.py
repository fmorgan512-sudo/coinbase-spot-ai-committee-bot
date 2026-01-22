from dataclasses import dataclass
from typing import Any
from .config import settings


@dataclass
class RiskState:
      daily_pnl_pct: float
      trades_last_hour: int
      exposure_pct: float


def validate_action(action: dict[str, Any], risk: RiskState) -> tuple[bool, str]:
      """
          Hard guardrails. The AI can suggest; this validator decides.
              """
      if risk.daily_pnl_pct <= -abs(settings.max_daily_loss_pct):
                return False, "Circuit breaker: max daily loss exceeded"

      if risk.trades_last_hour >= settings.max_trades_per_hour:
                return False, "Circuit breaker: max trades per hour exceeded"

      # Allow only risk-reducing actions by default
      allowed = {"reduce_position", "tighten_risk", "pause_trading", "cancel_orders"}
      if action.get("type") not in allowed:
                return False, f"Action type not allowed: {action.get('type')}"

      return True, "ok"
