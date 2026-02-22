---
name: mutazili-fatawa
description: Build and iterate a Quran-centric neo-Mutazili fatwa pipeline for quranqa.org. Use when scraping IslamQA.org question corpora, generating first-pass Mutazili draft rulings, refining jurisprudential principles, mapping verdict logic across madhhab variants, and producing structured datasets for scholar review.
---

# Mutazili Fatawa

## Overview

Run a two-stage workflow: scrape IslamQA.org entries into a local corpus, then generate Quran-first neo-Mutazili draft fatawa for manual refinement.

## Workflow

1. Confirm scope and storage roots.
2. Scrape IslamQA.org via sitemap feeds (skip IslamQA.info).
3. Build draft fatawa using the rules in `references/neo-mutazili-rubric.md`.
4. Save machine-readable artifacts for iterative review.
5. Tighten rubric and rerun.

## Commands

Run from repository root:

```bash
python scripts/run_pipeline.py --limit 2000 --workers 16 --storage-root D:\IslamQAScraping
```

Individual stages:

```bash
python scripts/scrape_islamqa_org.py --output D:\IslamQAScraping\islamqa_org_queries.jsonl --limit 2000 --workers 16
python scripts/generate_mutazili_fatawa.py --input D:\IslamQAScraping\islamqa_org_queries.jsonl --output D:\IslamQAScraping\mutazili_drafts.jsonl --limit 2000
```

## Expected Outputs

- `D:\IslamQAScraping\islamqa_org_queries.jsonl`: scraped source corpus
- `D:\IslamQAScraping\mutazili_drafts.jsonl`: first-pass neo-Mutazili drafts
- `D:\IslamQAScraping\quranqa.sqlite3`: queryable database for website/API

## Iteration Rules

- Keep rulings Quran-centric, reason-explicit, and welfare-aware.
- Mark all outputs as preliminary machine drafts.
- When user feedback changes doctrine, update rubric first and regenerate drafts.
- Prefer deterministic rule changes over ad-hoc per-row edits.

## References

- Use `references/neo-mutazili-rubric.md` for principle definitions and tuning points.
