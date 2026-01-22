AI_ACTION_ENUM = ["reduce_position", "tighten_risk", "pause_trading", "cancel_orders"]

# Shared JSON schema-like expectations (we enforce in code too).
RESPONSE_SHAPE = {
      "summary": "string",
      "risk_level": "low|medium|high",
      "actions": [
                {
                              "type": "|".join(AI_ACTION_ENUM),
                              "symbol": "string|null",
                              "pct": "number|null",
                              "reason": "string",
                              "confidence": "number (0..1)",
                }
      ],
}
