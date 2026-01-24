import sqlite3
from contextlib import contextmanager
from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    balances_json TEXT NOT NULL,
    orders_json TEXT NOT NULL,
    fills_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    trigger_reason TEXT NOT NULL,
    report_json TEXT NOT NULL,
    openai_json TEXT,
    anthropic_json TEXT,
    committee_json TEXT NOT NULL,
    applied INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    source_run_id INTEGER,
    action_json TEXT NOT NULL,
    executed INTEGER NOT NULL DEFAULT 0,
    result_json TEXT
);

CREATE TABLE IF NOT EXISTS config_kv (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    model TEXT NOT NULL,
    user_text TEXT NOT NULL,
    assistant_text TEXT NOT NULL,
    context_json TEXT NOT NULL
);
"""

def init_db():
    with connect() as con:
        con.executescript(SCHEMA)
        con.commit()


@contextmanager
def connect():
    con = sqlite3.connect(settings.db_path)
    try:
        yield con
    finally:
        con.close()
