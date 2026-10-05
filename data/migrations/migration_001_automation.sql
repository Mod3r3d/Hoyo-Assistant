-- Migration 001: Automation Layer Tables

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id INTEGER NOT NULL,
    game TEXT NOT NULL,
    uid INTEGER NOT NULL,
    cookie_encrypted TEXT NOT NULL,
    session_status TEXT NOT NULL DEFAULT 'VALID',
    last_auth_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(discord_user_id, game, uid)
);

CREATE TABLE IF NOT EXISTS automation_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER UNIQUE NOT NULL,
    discord_user_id INTEGER NOT NULL,
    automation_enabled BOOLEAN NOT NULL DEFAULT 1,
    checkin_enabled BOOLEAN NOT NULL DEFAULT 1,
    redeem_enabled BOOLEAN NOT NULL DEFAULT 1,
    mimo_enabled BOOLEAN NOT NULL DEFAULT 1,
    accompany_enabled BOOLEAN NOT NULL DEFAULT 0,
    event_notify_enabled BOOLEAN NOT NULL DEFAULT 1,
    notify_mode TEXT NOT NULL DEFAULT 'FAILURE_ONLY',
    notify_channel_id INTEGER DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS checkin_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    game TEXT NOT NULL,
    run_date TEXT NOT NULL,
    status TEXT NOT NULL,
    reward_summary TEXT DEFAULT NULL,
    error_code TEXT DEFAULT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, run_date)
);

CREATE TABLE IF NOT EXISTS gift_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    game TEXT NOT NULL,
    source TEXT NOT NULL,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT NULL,
    last_checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    UNIQUE(game, code)
);

CREATE TABLE IF NOT EXISTS giftcode_redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    gift_code_id INTEGER NOT NULL,
    game TEXT NOT NULL,
    code TEXT NOT NULL,
    status TEXT NOT NULL,
    response_msg TEXT DEFAULT NULL,
    redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, gift_code_id)
);

CREATE TABLE IF NOT EXISTS automation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    external_task_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    status TEXT NOT NULL,
    reward TEXT DEFAULT NULL,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP DEFAULT NULL,
    last_error TEXT DEFAULT NULL,
    UNIQUE(account_id, provider, external_task_id)
);

CREATE TABLE IF NOT EXISTS web_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL,
    game TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    banner_url TEXT DEFAULT NULL,
    start_at TIMESTAMP DEFAULT NULL,
    end_at TIMESTAMP DEFAULT NULL,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game, external_id)
);

CREATE TABLE IF NOT EXISTS automation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    game TEXT DEFAULT NULL,
    account_id INTEGER DEFAULT NULL,
    status TEXT NOT NULL,
    duration_ms INTEGER DEFAULT 0,
    message TEXT DEFAULT NULL,
    error_detail TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_game ON sessions(discord_user_id, game);
CREATE INDEX IF NOT EXISTS idx_checkin_account_date ON checkin_executions(account_id, run_date);
CREATE INDEX IF NOT EXISTS idx_giftcodes_active ON gift_codes(game, status);
CREATE INDEX IF NOT EXISTS idx_auto_logs_task ON automation_logs(task_name, status);
