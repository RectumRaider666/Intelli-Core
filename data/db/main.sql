-- <!-- [SS-0]: Intellicap Trading Fund Database Schema -->
-- SQLite Schema for rusqlite

-- <!-- [SS-1]: Server Management ----->,
-- /1.1/ Core Server
CREATE TABLE IF NOT EXISTS system (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_name TEXT NOT NULL,
    node TEXT NOT NULL CHECK(node IN ('parent', 'child')),
    node_uuid TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'maintenance', 'error')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    main_state TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_system_node ON system(node);
CREATE INDEX IF NOT EXISTS idx_system_status ON system(status);
CREATE INDEX IF NOT EXISTS idx_system_uuid ON system(node_uuid);
CREATE INDEX IF NOT EXISTS idx_system_server_name ON system(server_name);

-- /1.2/ Connections
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    server_id INTEGER NOT NULL,
    FOREIGN KEY (server_id) REFERENCES system(id) ON DELETE CASCADE,
    connected_at TEXT NOT NULL DEFAULT (datetime('now')),
    disconnected_at TEXT DEFAULT NULL,
    active INTEGER DEFAULT 0 CHECK(active IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_connections_server_id ON connections(server_id);
CREATE INDEX IF NOT EXISTS idx_connections_active ON connections(active);
CREATE INDEX IF NOT EXISTS idx_connections_ip ON connections(ip_address);

-- /1.3/ Authentication Requests
CREATE TABLE IF NOT EXISTS auth_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER NOT NULL,
    FOREIGN KEY (connection_id) REFERENCES connections(id) ON DELETE CASCADE,
    ip_address TEXT NOT NULL,
    server_id INTEGER NOT NULL,
    FOREIGN KEY (server_id) REFERENCES system(id) ON DELETE CASCADE,
    request_time TEXT NOT NULL DEFAULT (datetime('now')),
    result INTEGER DEFAULT 0 CHECK(result IN (0, 1)),
    content TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_auth_connection ON auth_requests(connection_id);
CREATE INDEX IF NOT EXISTS idx_auth_server ON auth_requests(server_id);
CREATE INDEX IF NOT EXISTS idx_auth_result ON auth_requests(result);
CREATE INDEX IF NOT EXISTS idx_auth_time ON auth_requests(request_time);

-- /1.4/ Logs
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    FOREIGN KEY (server_id) REFERENCES system(id) ON DELETE CASCADE,
    log_level TEXT NOT NULL CHECK(log_level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')),
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    content TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_logs_server ON logs(server_id);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(log_level);
CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at);

-- <!-- [SS-2]: User Management ----->
-- /2.1/ Users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL CHECK(length(username) <= 16),
    email TEXT UNIQUE NOT NULL,
    verified INTEGER DEFAULT 0 CHECK(verified IN (0, 1)),
    pass TEXT NOT NULL CHECK(length(pass) = 64),
    birthday TEXT NOT NULL,
    dev_status INTEGER DEFAULT 0 CHECK(dev_status IN (0, 1)),
    trade_status INTEGER DEFAULT 0 CHECK(trade_status IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_verified ON users(verified);
CREATE INDEX IF NOT EXISTS idx_users_dev_status ON users(dev_status);

-- /2.2/ Dev Keys
CREATE TABLE IF NOT EXISTS dev_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    dev_key TEXT UNIQUE NOT NULL CHECK(length(dev_key) = 128),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    revoked INTEGER DEFAULT 0 CHECK(revoked IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_dev_keys_user ON dev_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_dev_keys_key ON dev_keys(dev_key);
CREATE INDEX IF NOT EXISTS idx_dev_keys_revoked ON dev_keys(revoked);

-- /2.3/ User Wallets
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    internal INTEGER DEFAULT 1 CHECK(internal IN (0, 1)),
    pub_key TEXT UNIQUE NOT NULL CHECK(length(pub_key) = 128),
    priv_key TEXT NOT NULL CHECK(length(priv_key) = 128),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_wallets_user ON wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_wallets_pub_key ON wallets(pub_key);
CREATE INDEX IF NOT EXISTS idx_wallets_internal ON wallets(internal);

-- /2.4/ User Portfolios
CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    shares TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_portfolios_user ON portfolios(user_id);
