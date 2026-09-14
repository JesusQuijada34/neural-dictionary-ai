from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from .vectors import vector_for, tokenize

SCHEMA = """
CREATE TABLE IF NOT EXISTS concepts (
 id INTEGER PRIMARY KEY,
 term TEXT NOT NULL UNIQUE,
 category TEXT NOT NULL DEFAULT 'general',
 region TEXT,
 teaching TEXT,
 examples TEXT,
 vector TEXT NOT NULL,
 frequency INTEGER NOT NULL DEFAULT 1,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_concepts_category ON concepts(category);
CREATE INDEX IF NOT EXISTS idx_concepts_region ON concepts(region);
CREATE TABLE IF NOT EXISTS interactions (
 id INTEGER PRIMARY KEY,
 user_text TEXT NOT NULL,
 response TEXT NOT NULL,
 emotion TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

class LexicalMemory:
    def __init__(self, path: str | Path, dimensions: int = 64):
        self.path = Path(path)
        self.dimensions = dimensions
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    def add(self, term: str, category='general', region=None, teaching=None, examples=None) -> None:
        term = term.strip().lower()
        if not term:
            return
        self.db.execute("""INSERT INTO concepts(term, category, region, teaching, examples, vector)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(term) DO UPDATE SET category=excluded.category,
            region=excluded.region, teaching=excluded.teaching, examples=excluded.examples,
            frequency=concepts.frequency+1""", (term, category, region, teaching,
            json.dumps(examples or [], ensure_ascii=False), json.dumps(vector_for(term, self.dimensions))))
        self.db.commit()

    def bulk_add(self, records) -> int:
        for record in records:
            self.add(**record)
        return len(records)

    def all(self):
        return self.db.execute("SELECT * FROM concepts ORDER BY frequency DESC, term").fetchall()

    def search_tokens(self, text: str):
        tokens = tokenize(text)
        if not tokens:
            return []
        placeholders = ','.join('?' for _ in tokens)
        return self.db.execute(f"SELECT * FROM concepts WHERE term IN ({placeholders})", tokens).fetchall()

    def record_interaction(self, user_text, response, emotion):
        self.db.execute("INSERT INTO interactions(user_text,response,emotion) VALUES (?,?,?)", (user_text, response, emotion))
        self.db.commit()

    def close(self):
        self.db.close()
