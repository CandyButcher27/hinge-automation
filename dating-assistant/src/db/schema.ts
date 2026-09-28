export const SCHEMA = `
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_preferences_category
    ON preferences(category);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    occupation TEXT,
    location TEXT,
    bio TEXT,
    notes TEXT,
    user_rating INTEGER,
    fingerprint TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_fingerprint
    ON profiles(fingerprint);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,

    FOREIGN KEY(profile_id)
        REFERENCES profiles(id)
);

CREATE INDEX IF NOT EXISTS idx_conversations_profile
    ON conversations(profile_id);

CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER,
    draft TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL,

    FOREIGN KEY(profile_id)
        REFERENCES profiles(id)
);

CREATE INDEX IF NOT EXISTS idx_drafts_profile
    ON drafts(profile_id);
`;
