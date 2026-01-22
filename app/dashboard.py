import streamlit as st
import pandas as pd
import json
from app.core.db import init_db, connect
from app.core.config import settings

st.set_page_config(page_title="Coinbase AI Committee Bot", layout="wide")

init_db()


def fetch_df(query, params=()):
      with connect() as con:
                df = pd.read_sql_query(query, con, params=params)
            return df


st.title("Coinbase Spot Bot - Dashboard")

tabs = st.tabs(["Performance", "Positions", "AI Committee", "Logs", "Keys/Settings"])

with tabs[0]:
      st.subheader("Performance")
    df = fetch_df("SELECT ts, metrics_json FROM snapshots ORDER BY id DESC LIMIT 300")
    if df.empty:
              st.info("No data yet.")
else:
        df["metrics"] = df["metrics_json"].apply(json.loads)
          df["realized_usd"] = df["metrics"].apply(lambda x: x.get("realized_usd", 0.0))
        st.line_chart(df.sort_values("ts")[["realized_usd"]])

with tabs[1]:
      st.subheader("Latest snapshot")
    df = fetch_df("SELECT ts, balances_json, orders_json, metrics_json FROM snapshots ORDER BY id DESC LIMIT 1")
    if df.empty:
              st.info("No data yet.")
else:
        row = df.iloc[0]
        st.json(json.loads(row["metrics_json"]))
        st.json(json.loads(row["balances_json"]))
        st.json(json.loads(row["orders_json"]))

with tabs[2]:
      st.subheader("AI Committee Runs")
    df = fetch_df("SELECT ts, trigger_reason, committee_json, openai_json, anthropic_json FROM ai_runs ORDER BY id DESC LIMIT 50")
    if df.empty:
              st.info("No AI runs yet.")
else:
        for _, r in df.iterrows():
                      st.markdown(f"**{r['ts']}** - trigger: `{r['trigger_reason']}`")
                      st.json(json.loads(r["committee_json"]))
                      with st.expander("OpenAI raw"):
                                        st.json(json.loads(r["openai_json"]) if r["openai_json"] else {})
                                    with st.expander("Claude raw"):
                                                      st.json(json.loads(r["anthropic_json"]) if r["anthropic_json"] else {})
                                                  st.divider()

with tabs[3]:
      st.subheader("Actions Log")
    df = fetch_df("SELECT ts, action_json, executed, result_json FROM actions ORDER BY id DESC LIMIT 200")
    if df.empty:
              st.info("No actions logged.")
else:
        st.dataframe(df, use_container_width=True)

with tabs[4]:
      st.subheader("Keys / Settings")
    st.warning("For safety, keys should be set via environment variables or a secret manager. This panel is informational in v1.")
    st.code(f"DRY_RUN={settings.dry_run}\nPOLL_SECONDS={settings.poll_seconds}\nAI_MIN_SECONDS_BETWEEN={settings.ai_min_seconds_between}")
    st.info("To change keys/settings, edit .env and restart containers.")
