from __future__ import annotations
import time
from app.core.config import settings
from app.core.db import init_db, connect
from app.core.coinbase_client import CoinbaseClient
from app.core.pnl import compute_realized_from_fills, pct_change
from app.core.utils import now_ts, dumps
from app.core.llm_openai import analyze_report as openai_analyze
from app.core.llm_anthropic import analyze_report as anthropic_analyze
from app.core.committee import committee_decide
from app.core.risk import RiskState, validate_action


def load_last_metrics():
      with connect() as con:
                row = con.execute("SELECT metrics_json FROM snapshots ORDER BY id DESC LIMIT 1").fetchone()
                if not row:
                              return None
                          import json
                return json.loads(row[0])


def should_call_ai(last_metrics, new_metrics, last_ai_ts: int) -> tuple[bool, str]:
      now = now_ts()
      if now - last_ai_ts >= settings.ai_min_seconds_between:
                return True, "periodic"
            if last_metrics is None:
                      return True, "first_run"
                  # triggers
                  pnl_last = float(last_metrics.get("realized_usd", 0.0))
    pnl_new = float(new_metrics.get("realized_usd", 0.0))
    if abs(pct_change(pnl_last, pnl_new)) >= settings.pnl_delta_trigger_pct:
              return True, "realized_pnl_delta"
          return False, "no_trigger"


def main():
      init_db()
    cb = CoinbaseClient()
    last_ai_ts = 0

    while True:
              ts = now_ts()
              try:
                            balances = cb.get_accounts()
                            orders = cb.list_orders(limit=50)
                            fills = cb.list_fills(limit=200)
        except Exception as e:
            print("Coinbase fetch error:", repr(e))
            time.sleep(settings.poll_seconds)
            continue

        pnl = compute_realized_from_fills(fills, quote_ccy=settings.quote_currency)
        metrics = {
                      "realized_usd": pnl.realized_usd,
                      "num_fills": pnl.num_fills,
                      "ts": ts,
        }

        with connect() as con:
                      con.execute(
                                        "INSERT INTO snapshots (ts, balances_json, orders_json, fills_json, metrics_json) VALUES (?,?,?,?,?)",
                                        (ts, dumps(balances), dumps(orders), dumps(fills), dumps(metrics)),
                      )
                      con.commit()

        last_metrics = load_last_metrics()
        call_ai, reason = should_call_ai(last_metrics, metrics, last_ai_ts)

        if call_ai:
                      report = {
                                        "ts": ts,
                                        "metrics": metrics,
                                        "balances": balances,
                                        "orders": orders,
                                        "recent_fills": fills,
                                        "policy": {
                                                              "allowed_actions": ["reduce_position", "tighten_risk", "pause_trading", "cancel_orders"],
                                                              "never": ["increase_exposure", "remove_risk_limits", "leverage_up"],
                                        }
                      }
                      oa = openai_analyze(report)
                      ca = anthropic_analyze(report)
                      committee = committee_decide(oa, ca)

            with connect() as con:
                              con.execute(
                                                    "INSERT INTO ai_runs (ts, trigger_reason, report_json, openai_json, anthropic_json, committee_json) VALUES (?,?,?,?,?,?)",
                                                    (ts, reason, dumps(report), dumps(oa), dumps(ca), dumps(committee)),
                              )
                              run_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
                              con.commit()

            # Apply agreed actions if pass validator
            risk = RiskState(
                              daily_pnl_pct=0.0,  # TODO: compute from equity curve
                              trades_last_hour=0,  # TODO: compute from actions table timestamps
                              exposure_pct=0.0,  # TODO: compute from balances
            )

            for action in committee.get("agreed_actions", []):
                              ok, why = validate_action(action, risk)
                              print("ACTION", action, "VALID", ok, why)
                              with connect() as con:
                                                    con.execute(
                                                                              "INSERT INTO actions (ts, source_run_id, action_json, executed, result_json) VALUES (?,?,?,?,?)",
                                                                              (ts, run_id, dumps(action), 0, dumps({"validated": ok, "why": why})),
                                                    )
                                                    con.commit()
                                                if not ok:
                                                                      continue
                                                                  if settings.dry_run:
                                                                                        print("DRY_RUN: would execute", action)
                                                                                        continue
                                                                                    # TODO: map actions -> concrete order changes

            last_ai_ts = ts

        time.sleep(settings.poll_seconds)


if __name__ == "__main__":
      main()
