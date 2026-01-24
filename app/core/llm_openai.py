from __future__ import annotations
from typing import Any, Dict
from openai import OpenAI
from .config import settings

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def analyze_report(report: Dict[str, Any]) -> Dict[str, Any]:
    if client is None:
        return {"summary": "OpenAI key missing", "risk_level": "high", "actions": []}

    prompt = (
        "You are a risk-first trading advisor for Coinbase spot trading.\n"
        "Return ONLY JSON with keys: summary, risk_level, actions.\n"
        "Allowed action types: reduce_position, tighten_risk, pause_trading, cancel_orders.\n"
        "Never suggest increasing exposure/leverage.\n"
        "If unsure or data insufficient, return no actions.\n"
        f"REPORT:\n{report}"
    )

    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    text = resp.choices[0].message.content if resp.choices else ""
    import json
    try:
        return json.loads(text)
    except Exception:
        return {"summary": "OpenAI returned non-JSON", "risk_level": "high", "actions": []}
