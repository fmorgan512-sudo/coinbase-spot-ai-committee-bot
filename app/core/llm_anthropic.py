from __future__ import annotations
from typing import Any, Dict
import anthropic
from .config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None


def analyze_report(report: Dict[str, Any]) -> Dict[str, Any]:
      if client is None:
                return {"summary": "Anthropic key missing", "risk_level": "high", "actions": []}

      prompt = (
          "You are a risk-first trading advisor for Coinbase spot trading.\n"
          "Return ONLY JSON with keys: summary, risk_level, actions.\n"
          "Allowed action types: reduce_position, tighten_risk, pause_trading, cancel_orders.\n"
          "Never suggest increasing exposure/leverage.\n"
          "If unsure, return no actions.\n"
          f"REPORT:\n{report}"
      )

    msg = client.messages.create(
              model=settings.anthropic_model,
              max_tokens=800,
              temperature=0.2,
              messages=[{"role": "user", "content": prompt}],
    )

    text = msg.content[0].text if msg.content else ""
    import json
    try:
              return json.loads(text)
except Exception:
          return {"summary": "Claude returned non-JSON", "risk_level": "high", "actions": []}
