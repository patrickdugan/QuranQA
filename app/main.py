#!/usr/bin/env python3
"""FastAPI app for QuranQA draft fatawa browsing and feedback."""

from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
DB_PATH = Path(os.getenv("QURANQA_DB_PATH", r"D:\IslamQAScraping\quranqa.sqlite3"))

app = FastAPI(title="QuranQA")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/web", StaticFiles(directory=str(WEB_DIR)), name="web")


def get_conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail=f"DB not found: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class FeedbackIn(BaseModel):
    fatwa_id: int
    comment: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/topics")
def topics() -> dict:
    conn = get_conn()
    rows = conn.execute(
        "SELECT topic, COUNT(*) AS n FROM fatawa GROUP BY topic ORDER BY n DESC"
    ).fetchall()
    conn.close()
    return {"topics": [{"topic": r["topic"], "count": r["n"]} for r in rows]}


@app.get("/api/fatawa")
def list_fatawa(
    topic: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(30, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict:
    conn = get_conn()
    where = []
    params = []
    if topic:
        where.append("topic = ?")
        params.append(topic)
    if q:
        where.append("(title LIKE ? OR question_summary LIKE ? OR draft_fatwa_text LIKE ?)")
        needle = f"%{q}%"
        params.extend([needle, needle, needle])

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    rows = conn.execute(
        f"""
        SELECT id, url, title, question_summary, topic
        FROM fatawa
        {where_sql}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        [*params, limit, offset],
    ).fetchall()
    total = conn.execute(
        f"SELECT COUNT(*) AS n FROM fatawa {where_sql}",
        params,
    ).fetchone()["n"]
    conn.close()
    return {"total": total, "items": [dict(r) for r in rows]}


@app.get("/api/fatawa/{fatwa_id}")
def get_fatwa(fatwa_id: int) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT * FROM fatawa WHERE id = ?", (fatwa_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="fatwa not found")
    feedback = conn.execute(
        """
        SELECT id, comment, created_at_unix
        FROM feedback
        WHERE fatwa_id = ?
        ORDER BY id DESC
        LIMIT 50
        """,
        (fatwa_id,),
    ).fetchall()
    conn.close()
    payload = dict(row)
    payload["feedback"] = [dict(x) for x in feedback]
    return payload


@app.post("/api/feedback")
def add_feedback(data: FeedbackIn) -> dict:
    comment = (data.comment or "").strip()
    if not comment:
        raise HTTPException(status_code=400, detail="comment is required")
    conn = get_conn()
    exists = conn.execute("SELECT id FROM fatawa WHERE id = ?", (data.fatwa_id,)).fetchone()
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="fatwa not found")
    with conn:
        conn.execute(
            "INSERT INTO feedback (fatwa_id, comment, created_at_unix) VALUES (?, ?, ?)",
            (data.fatwa_id, comment, int(time.time())),
        )
    conn.close()
    return {"ok": True}
