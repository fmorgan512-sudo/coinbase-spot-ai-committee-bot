from __future__ import annotations
from typing import Any
from .schemas import AI_ACTION_ENUM


def normalize_actions(resp: dict[str, Any]) -> list[dict[str, Any]]:
    actions = resp.get("actions", []) if isinstance(resp, dict) else []
    out = []
    for a in actions:
        if not isinstance(a, dict):
            continue
        t = a.get("type")
        if t not in AI_ACTION_ENUM:
            continue
        out.append({
            "type": t,
            "symbol": a.get("symbol"),
            "pct": a.get("pct"),
            "reason": str(a.get("reason", ""))[:500],
            "confidence": float(a.get("confidence", 0.0) or 0.0),
        })
    return out


def committee_decide(openai_resp: dict[str, Any], anthropic_resp: dict[str, Any]) -> dict[str, Any]:
    """
    Conservative committee: only recommend actions that both models agree on
    by type+symbol, and take min(confidence).
    """
    oa = normalize_actions(openai_resp)
    ca = normalize_actions(anthropic_resp)

    index = {(a["type"], a.get("symbol")): a for a in oa}
    agreed = []
    for b in ca:
        key = (b["type"], b.get("symbol"))
        if key in index:
            a = index[key]
            agreed.append({
                "type": b["type"],
                "symbol": b.get("symbol"),
                "pct": b.get("pct") if b.get("pct") is not None else a.get("pct"),
                "reason": f"OA: {a['reason']} | CA: {b['reason']}",
                "confidence": min(a["confidence"], b["confidence"]),
            })

    return {
        "agreed_actions": sorted(agreed, key=lambda x: x["confidence"], reverse=True),
        "disagreed": len(oa) != len(ca) or len(agreed) == 0
    }
