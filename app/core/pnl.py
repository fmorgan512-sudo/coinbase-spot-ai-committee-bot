from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import math


@dataclass
class PnLMetrics:
      realized_usd: float
      num_fills: int


def compute_realized_from_fills(fills_payload: dict[str, Any], quote_ccy: str = "USD") -> PnLMetrics:
      """
          Minimal realized PnL approximation from fills.
              For production you'll want FIFO/average-cost accounting per asset.
                  """
      fills = fills_payload.get("fills", []) or fills_payload.get("data", []) or []
      # Placeholder: just sum fees as negative realized until you implement full inventory PnL.
      fees = 0.0
      for f in fills:
          fee = f.get("commission") or f.get("fee") or f.get("fees") or 0
                try:
                              fees += float(fee)
except Exception:
            pass
    return PnLMetrics(realized_usd=-fees, num_fills=len(fills))


def pct_change(a: float, b: float) -> float:
      if a == 0:
                return 0.0 if b == 0 else 100.0
            return (b - a) / abs(a) * 100.0


def safe_float(x, default=0.0) -> float:
      try:
                if x is None:
                              return default
                          v = float(x)
        if math.isnan(v) or math.isinf(v):
                      return default
                  return v
except Exception:
        return default
