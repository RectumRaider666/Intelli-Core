CREATE TABLE IF NOT EXISTS items (
    -- Non Nullable
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    type TEXT NOT NULL,
    tradable BOOLEAN NOT NULL DEFAULT TRUE,
    findable BOOLEAN NOT NULL DEFAULT TRUE,

    -- Nullable
    subtype TEXT,
    requirement TEXT,
    effect TEXT
);

CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    location TEXT,
    buy INTEGER,
    sell INTEGER,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE TABLE IF NOT EXISTS circulation(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    circulation INTEGER NOT NULL,
    date TEXT NOT NULL,
    fair_value INTEGER,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    price INTEGER NOT NULL,
    volume INTEGER NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);
