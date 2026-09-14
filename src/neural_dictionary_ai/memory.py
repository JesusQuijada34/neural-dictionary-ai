from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from .vectors import vector_for, numeric_spelling, tokenize

SCHEMA = """
CREATE TABLE IF NOT EXISTS concepts (
 id INTEGER PRIMARY KEY, term TEXT NOT NULL UNIQUE, category TEXT NOT NULL DEFAULT 'general',
 region TEXT, teaching TEXT, examples TEXT, numeric_spelling TEXT NOT NULL DEFAULT '[]',
 vector TEXT NOT NULL, frequency INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_concepts_category ON concepts(category);
CREATE INDEX IF NOT EXISTS idx_concepts_region ON concepts(region);
CREATE TABLE IF NOT EXISTS relations (
 id INTEGER PRIMARY KEY, source TEXT NOT NULL, relation TEXT NOT NULL, target TEXT NOT NULL,
 weight REAL NOT NULL DEFAULT 1.0, UNIQUE(source, relation, target)
);
CREATE TABLE IF NOT EXISTS user_memory (
 id INTEGER PRIMARY KEY, key TEXT NOT NULL UNIQUE, value TEXT NOT NULL, confidence REAL NOT NULL DEFAULT 0.5,
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS interactions (
 id INTEGER PRIMARY KEY, user_text TEXT NOT NULL, response TEXT NOT NULL, emotion TEXT NOT NULL,
 confidence REAL NOT NULL DEFAULT 0.0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

class LexicalMemory:
    def __init__(self, path: str | Path, dimensions: int = 64):
        self.path = Path(path); self.dimensions = dimensions; self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path); self.db.row_factory = sqlite3.Row; self.db.executescript(SCHEMA)
        self._add_column_if_missing("concepts", "numeric_spelling", "TEXT NOT NULL DEFAULT '[]'")
        self._add_column_if_missing("interactions", "confidence", "REAL NOT NULL DEFAULT 0.0"); self.db.commit()

    def _add_column_if_missing(self, table, column, definition):
        columns = {row[1] for row in self.db.execute(f"PRAGMA table_info({table})")}
        if column not in columns: self.db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def add(self, term: str, category='general', region=None, teaching=None, examples=None) -> None:
        term = term.strip().lower()
        if not term: return
        self.db.execute("""INSERT INTO concepts(term,category,region,teaching,examples,numeric_spelling,vector)
        VALUES(?,?,?,?,?,?,?) ON CONFLICT(term) DO UPDATE SET category=excluded.category,region=excluded.region,
        teaching=excluded.teaching,examples=excluded.examples,numeric_spelling=excluded.numeric_spelling,
        vector=excluded.vector,frequency=concepts.frequency+1""", (term,category,region,teaching,
        json.dumps(examples or [], ensure_ascii=False),json.dumps(numeric_spelling(term)),json.dumps(vector_for(term,self.dimensions))))
        self.db.commit()

    def add_relation(self, source, relation, target, weight=1.0):
        self.db.execute("INSERT OR REPLACE INTO relations(source,relation,target,weight) VALUES(?,?,?,?)", (source.lower(),relation,target.lower(),weight)); self.db.commit()

    def relations_for(self, terms):
        if not terms: return []
        marks = ','.join('?' for _ in terms)
        return self.db.execute(f"SELECT * FROM relations WHERE source IN ({marks}) OR target IN ({marks})", list(terms)+list(terms)).fetchall()

    def remember_user(self, key, value, confidence=0.7):
        self.db.execute("INSERT INTO user_memory(key,value,confidence) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,confidence=excluded.confidence,updated_at=CURRENT_TIMESTAMP", (key,value,confidence)); self.db.commit()

    def user_facts(self): return self.db.execute("SELECT * FROM user_memory ORDER BY updated_at DESC").fetchall()
    def bulk_add(self, records) -> int:
        for record in records: self.add(**record)
        return len(records)
    def all(self): return self.db.execute("SELECT * FROM concepts ORDER BY frequency DESC,term").fetchall()
    def search_tokens(self, text: str):
        tokens = tokenize(text)
        if not tokens: return []
        marks=','.join('?' for _ in tokens); return self.db.execute(f"SELECT * FROM concepts WHERE term IN ({marks})",tokens).fetchall()
    def record_interaction(self,user_text,response,emotion,confidence=0.0):
        self.db.execute("INSERT INTO interactions(user_text,response,emotion,confidence) VALUES(?,?,?,?)",(user_text,response,emotion,confidence)); self.db.commit()

    def export_json(self, path: str | Path):
        payload={"format":"neural-dictionary-ai/1","concepts":[dict(row) for row in self.all()],"relations":[dict(row) for row in self.db.execute("SELECT source,relation,target,weight FROM relations ORDER BY source,relation,target")]}
        Path(path).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8"); return payload

    def import_json(self, path: str | Path) -> dict:
        payload=json.loads(Path(path).read_text(encoding="utf-8"))
        for row in payload.get("concepts",[]):
            examples=row.get("examples",[]); examples=json.loads(examples) if isinstance(examples,str) else examples
            self.add(row["term"],row.get("category","general"),row.get("region"),row.get("teaching"),examples)
        for row in payload.get("relations",[]): self.add_relation(row["source"],row["relation"],row["target"],row.get("weight",1.0))
        return {"concepts":len(payload.get("concepts",[])),"relations":len(payload.get("relations",[]))}

    def close(self): self.db.close()
