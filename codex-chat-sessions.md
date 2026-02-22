# Codex Chat Sessions

## 2026-02-22 - QuranQA Bootstrap + MutaziliFiqh Baseline

### User Intent

Start a repo/project/skill for quranqa.org, scrape IslamQA.org (excluding IslamQA.info), generate neo-Mutazili Quran-centric draft fatawa, then iterate toward multi-madhhab support.

### Actions Completed

- Initialized project structure in `C:\projects\QuranQA`.
- Added `mutazili-fatawa` skill and operational references.
- Created `D:\IslamQAScraping` data root and scraped 2000 IslamQA.org entries.
- Generated 2000 draft fatawa using rule-based neo-Mutazili framing.
- Built local SQLite database and web app (FastAPI + static frontend) for browse/search/feedback.
- Encoded doctrinal updates from user (riba, prayer, marriage/divorce, gambling/trading, diet, intoxicants, medical flexibility).
- Added position-fatwa module for sectarian ethics, Mutazili-Kaysani framing, and AI ethics/safety-as-jihad.
- Initialized git repo and committed implementation.

### Key Outputs

- `D:\IslamQAScraping\islamqa_org_queries.jsonl` (2000)
- `D:\IslamQAScraping\mutazili_drafts.jsonl` (2000)
- `D:\IslamQAScraping\quranqa.sqlite3`

### Commits

- `15eb4c6` Bootstrap MutaziliFatawa pipeline, DB, and web app
- `f048c59` Add position fatawa for sectarian ethics and AI jihad framing

### Notes

`mutazili-fatawa` is currently serving as the MutaziliFiqh skill namespace for this repo.
