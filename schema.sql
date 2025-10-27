-- schema.sql
CREATE TABLE IF NOT EXISTS subscriptions (
  id SERIAL PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  phone TEXT,
  status TEXT CHECK (status IN ('active','expired')) NOT NULL DEFAULT 'active',
  start_date TIMESTAMPTZ,
  expiry_date TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS engagement (
  id SERIAL PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  messages_count INTEGER NOT NULL DEFAULT 0,
  last_seen TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS uploads (
  id SERIAL PRIMARY KEY,
  uploader_id BIGINT NOT NULL,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  free_or_paid TEXT CHECK (free_or_paid IN ('free','paid')) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
