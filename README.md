# QuranQA Bootstrap

Initial pipeline for `quranqa.org` data ingestion and neo-Mutazili draft generation.

## Scope

- Scrape question pages from `https://islamqa.org` via sitemap.
- Skip `islamqa.info`.
- Store corpus and generated drafts under `D:\IslamQAScraping`.

## Setup

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python scripts/run_pipeline.py --limit 2000 --workers 16 --storage-root D:\IslamQAScraping
```

Build SQLite DB:

```bash
python scripts/build_sqlite_db.py --scraped D:\IslamQAScraping\islamqa_org_queries.jsonl --drafts D:\IslamQAScraping\mutazili_drafts.jsonl --db D:\IslamQAScraping\quranqa.sqlite3
```

Run website:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Outputs

- `D:\IslamQAScraping\islamqa_org_queries.jsonl`
- `D:\IslamQAScraping\mutazili_drafts.jsonl`
- `D:\IslamQAScraping\quranqa.sqlite3`

## Notes

- Generated fatwa text is draft-only and intended for iterative human correction.
- Jurisprudential tuning reference: `skills/mutazili-fatawa/references/neo-mutazili-rubric.md`.
