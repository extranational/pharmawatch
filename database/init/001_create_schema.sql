-- SQL init for pharmaceutical signal database

CREATE TABLE IF NOT EXISTS raw_signals (
    id          TEXT PRIMARY KEY,
    source      TEXT NOT NULL,
    title       TEXT,
    category    TEXT DEFAULT 'unknown',
    raw_data    JSONB,
    received_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS normalized_signals (
    id              TEXT PRIMARY KEY,
    raw_signal_id   TEXT REFERENCES raw_signals(id),
    title           TEXT,
    category        TEXT,
    normalized_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS enriched_signals (
    id              TEXT PRIMARY KEY,
    normalized_id   TEXT REFERENCES normalized_signals(id),
    enrichment      JSONB,
    enriched_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synthesized_signals (
    id              TEXT PRIMARY KEY,
    enriched_id     TEXT REFERENCES enriched_signals(id),
    summary         TEXT,
    key_insights    TEXT[],
    confidence      REAL DEFAULT 0.0,
    synthesized_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_signals_source  ON raw_signals(source);
CREATE INDEX IF NOT EXISTS idx_raw_signals_category ON raw_signals(category);
CREATE INDEX IF NOT EXISTS idx_syn_confidence      ON synthesized_signals(confidence);
CREATE INDEX IF NOT EXISTS idx_syn_category         ON synthesized_signals(category);