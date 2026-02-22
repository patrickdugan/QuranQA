#!/usr/bin/env python3
"""Build a SQLite database from scraped and generated JSONL files."""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path


DDL = """
CREATE TABLE IF NOT EXISTS fatawa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    question_summary TEXT,
    source_answer TEXT,
    raw_text TEXT,
    topic TEXT,
    draft_fatwa_text TEXT,
    quran_references_json TEXT,
    principles_json TEXT,
    madhhab TEXT,
    source_org TEXT,
    generated_at_unix INTEGER,
    scraped_at_unix INTEGER,
    created_at_unix INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fatawa_topic ON fatawa(topic);
CREATE INDEX IF NOT EXISTS idx_fatawa_madhhab ON fatawa(madhhab);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fatwa_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at_unix INTEGER NOT NULL,
    FOREIGN KEY (fatwa_id) REFERENCES fatawa(id)
);
"""


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SQLite DB from QuranQA files")
    parser.add_argument("--scraped", required=True, help="Path to islamqa_org_queries.jsonl")
    parser.add_argument("--drafts", required=True, help="Path to mutazili_drafts.jsonl")
    parser.add_argument("--db", required=True, help="Output SQLite file path")
    args = parser.parse_args()

    scraped_path = Path(args.scraped)
    drafts_path = Path(args.drafts)
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    scraped_rows = load_jsonl(scraped_path)
    draft_rows = load_jsonl(drafts_path)
    by_url = {row.get("url"): row for row in scraped_rows if row.get("url")}

    conn = sqlite3.connect(db_path)
    conn.executescript(DDL)

    now = int(time.time())
    upsert_sql = """
    INSERT INTO fatawa (
        url, title, question_summary, source_answer, raw_text, topic, draft_fatwa_text,
        quran_references_json, principles_json, madhhab, source_org,
        generated_at_unix, scraped_at_unix, created_at_unix
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(url) DO UPDATE SET
        title=excluded.title,
        question_summary=excluded.question_summary,
        source_answer=excluded.source_answer,
        raw_text=excluded.raw_text,
        topic=excluded.topic,
        draft_fatwa_text=excluded.draft_fatwa_text,
        quran_references_json=excluded.quran_references_json,
        principles_json=excluded.principles_json,
        madhhab=excluded.madhhab,
        source_org=excluded.source_org,
        generated_at_unix=excluded.generated_at_unix,
        scraped_at_unix=excluded.scraped_at_unix;
    """

    inserted = 0
    with conn:
        for draft in draft_rows:
            url = draft.get("url")
            if not url:
                continue
            src = by_url.get(url, {})
            conn.execute(
                upsert_sql,
                (
                    url,
                    draft.get("title") or src.get("title"),
                    draft.get("question_summary") or src.get("question"),
                    src.get("source_answer", ""),
                    src.get("raw_text", ""),
                    draft.get("topic", ""),
                    draft.get("draft_fatwa_text", ""),
                    json.dumps(draft.get("quran_references", []), ensure_ascii=False),
                    json.dumps(draft.get("neo_mutazili_principles", []), ensure_ascii=False),
                    src.get("madhhab", ""),
                    src.get("source", ""),
                    draft.get("generated_at_unix"),
                    src.get("scraped_at_unix"),
                    now,
                ),
            )
            inserted += 1

    total = conn.execute("SELECT COUNT(*) FROM fatawa").fetchone()[0]
    conn.close()
    print(f"done inserted_or_updated={inserted} total={total} db={db_path}")


if __name__ == "__main__":
    main()
