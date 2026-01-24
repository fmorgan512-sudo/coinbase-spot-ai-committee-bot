import streamlit as st
import pandas as pd
import json
from core.db import init_db, connect
from core.config import settings
from core.key_store import save_keys, load_keys, keys_exist, delete_keys

st.set_page_config(page_title="Coinbase AI Committee Bot", layout="wide")

init_db()

# Session state for unlock status
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "stored_keys" not in st.session_state:
    st.session_state.stored_keys = None


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
    st.subheader("API Keys & Settings")

    st.warning("Keys are encrypted at rest using your password. Never share your password.")

    # Check if keys exist
    has_keys = keys_exist()

    if has_keys and not st.session_state.unlocked:
        st.info("Encrypted keys found. Enter password to unlock.")
        unlock_password = st.text_input("Password to unlock keys", type="password", key="unlock_pwd")
        if st.button("Unlock Keys"):
            loaded = load_keys(unlock_password)
            if loaded:
                st.session_state.unlocked = True
                st.session_state.stored_keys = loaded
                st.success("Keys unlocked successfully!")
                st.rerun()
            else:
                st.error("Invalid password or corrupted keys.")

    elif st.session_state.unlocked and st.session_state.stored_keys:
        st.success("Keys unlocked!")
        keys = st.session_state.stored_keys

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Coinbase CDP**")
            st.text(f"Key Name: {keys.get('coinbase_api_key_name', '')[:30]}...")
            st.text(f"Private Key: {'*' * 20} (stored)")
        with col2:
            st.markdown("**LLM APIs**")
            st.text(f"OpenAI: {'*' * 10}...{keys.get('openai_api_key', '')[-4:] if keys.get('openai_api_key') else 'Not set'}")
            st.text(f"Anthropic: {'*' * 10}...{keys.get('anthropic_api_key', '')[-4:] if keys.get('anthropic_api_key') else 'Not set'}")

        if st.button("Lock Keys"):
            st.session_state.unlocked = False
            st.session_state.stored_keys = None
            st.rerun()

        st.divider()
        st.subheader("Update Keys")

    else:
        st.info("No keys stored yet. Enter your API keys below.")

    # Key entry form (shown when unlocked or no keys exist)
    if st.session_state.unlocked or not has_keys:
        with st.form("key_form"):
            st.markdown("### Enter API Keys")

            st.markdown("**Coinbase CDP Credentials**")
            coinbase_key_name = st.text_input(
                "Coinbase API Key Name",
                value=st.session_state.stored_keys.get("coinbase_api_key_name", "") if st.session_state.stored_keys else "",
                placeholder="organizations/.../apiKeys/..."
            )
            coinbase_private_key = st.text_area(
                "Coinbase Private Key (PEM)",
                value=st.session_state.stored_keys.get("coinbase_api_private_key_pem", "") if st.session_state.stored_keys else "",
                placeholder="-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----",
                height=150
            )

            st.markdown("**LLM API Keys**")
            openai_key = st.text_input(
                "OpenAI API Key",
                value=st.session_state.stored_keys.get("openai_api_key", "") if st.session_state.stored_keys else "",
                type="password",
                placeholder="sk-..."
            )
            anthropic_key = st.text_input(
                "Anthropic API Key",
                value=st.session_state.stored_keys.get("anthropic_api_key", "") if st.session_state.stored_keys else "",
                type="password",
                placeholder="sk-ant-..."
            )

            st.markdown("**Encryption Password**")
            new_password = st.text_input(
                "Password to encrypt keys",
                type="password",
                placeholder="Enter a strong password",
                key="new_pwd"
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Confirm your password",
                key="confirm_pwd"
            )

            submitted = st.form_submit_button("Save Keys")

            if submitted:
                if not new_password:
                    st.error("Password is required to encrypt keys.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    keys_to_save = {
                        "coinbase_api_key_name": coinbase_key_name,
                        "coinbase_api_private_key_pem": coinbase_private_key,
                        "openai_api_key": openai_key,
                        "anthropic_api_key": anthropic_key,
                    }
                    if save_keys(new_password, keys_to_save):
                        st.session_state.unlocked = True
                        st.session_state.stored_keys = keys_to_save
                        st.success("Keys saved and encrypted successfully!")
                        st.info("Restart the worker container to use the new keys.")
                    else:
                        st.error("Failed to save keys.")

    st.divider()

    # Danger zone
    with st.expander("Danger Zone", expanded=False):
        st.warning("These actions cannot be undone!")
        if st.button("Delete All Stored Keys", type="primary"):
            if delete_keys():
                st.session_state.unlocked = False
                st.session_state.stored_keys = None
                st.success("All keys deleted.")
                st.rerun()
            else:
                st.error("Failed to delete keys.")

    st.divider()
    st.subheader("Current Settings (from environment)")
    st.code(f"DRY_RUN={settings.dry_run}\nPOLL_SECONDS={settings.poll_seconds}\nAI_MIN_SECONDS_BETWEEN={settings.ai_min_seconds_between}")
