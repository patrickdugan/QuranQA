# Session Notes (2026-02-22)

## Scope Completed

- Bootstrapped `QuranQA` repo in `C:\projects\QuranQA`.
- Created `mutazili-fatawa` skill as the working MutaziliFiqh skill.
- Created scraping storage root: `D:\IslamQAScraping`.
- Scraped 2000 IslamQA.org question pages (excluding IslamQA.info).
- Generated 2000 neo-Mutazili draft fatawa records.
- Built SQLite DB and local FastAPI + static web UI.

## User Doctrine Inputs Captured

- Riba: major injustice due to risk transfer and wealth concentration; avoid as jihad-like moral struggle.
- Finance alternatives: equity-style participation, murabaha/share-buyback style structures.
- Prayer: Ibn Masud tashahhud with `ala Nabi`, shortened 2nd-rakat tashahhud, Quran 10:10 preface framing, close with Alhamdulillah.
- Marriage/divorce: mutah halal; secret second marriage rejected as unfair; release with fairness/consent.
- Urfi treatment for non-Muslim exclusive relationships not auto-collapsed into zina.
- Divorce ethics: no cruel expulsion from homes; integrate Injil ethical warning frame (Mark 10 attribution uncertainty acknowledged).
- Gambling/trading: maisir haram; +EV disciplined trading can be mubah; options/algo trading can be mubah under bounded risk.
- Diet: mustahabb Jafari strictness, mubah Hanafi latitude.
- Intoxicants: alcohol haram; weed makruh baseline via medical-rational framing.
- Medical necessity: broader flexibility via inductive reasoning; cautious openness re trans care.

## Additional Position Fatawa Added

- Other sects/beliefs: critique allowed, dehumanization prohibited.
- Anti-sectarianism: communal obligation.
- Mutazili-Kaysani intersection: evidence-based historical hypothesis, not excommunication tool.
- AI usage: use-based ethics.
- AI safety research: nonviolent jihad/harm prevention framing.

## Artifacts

- Skill docs: `skills/mutazili-fatawa/SKILL.md`
- Rubric: `skills/mutazili-fatawa/references/neo-mutazili-rubric.md`
- Position notes: `skills/mutazili-fatawa/references/position-fatawa-v1.md`
- Generator: `scripts/generate_mutazili_fatawa.py`
- Scraper: `scripts/scrape_islamqa_org.py`
- DB builder: `scripts/build_sqlite_db.py`
- App: `app/main.py`, `web/index.html`, `web/app.js`, `web/styles.css`
- Data outputs: `D:\IslamQAScraping\islamqa_org_queries.jsonl`, `D:\IslamQAScraping\mutazili_drafts.jsonl`, `D:\IslamQAScraping\quranqa.sqlite3`

## Open Next Iteration

- Add reviewer confidence + `needs_human_review` flags.
- Add formal profiles for Twelver, Zaydi, and Quran-only tracks.
- Add feedback-to-rules loop so comments auto-generate rule diffs.
