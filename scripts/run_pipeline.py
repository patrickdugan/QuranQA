#!/usr/bin/env python3
"""Run scrape + draft generation pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QuranQA initial data pipeline")
    parser.add_argument("--limit", type=int, default=2000, help="How many queries to scrape/generate")
    parser.add_argument("--workers", type=int, default=16, help="Parallel workers for scraper")
    parser.add_argument(
        "--storage-root",
        default=r"D:\IslamQAScraping",
        help="Root directory for scraped + generated outputs",
    )
    args = parser.parse_args()

    root = Path(args.storage_root)
    root.mkdir(parents=True, exist_ok=True)

    scraped = root / "islamqa_org_queries.jsonl"
    drafts = root / "mutazili_drafts.jsonl"

    run(
        [
            sys.executable,
            "scripts/scrape_islamqa_org.py",
            "--output",
            str(scraped),
            "--limit",
            str(args.limit),
            "--workers",
            str(args.workers),
        ]
    )
    run(
        [
            sys.executable,
            "scripts/generate_mutazili_fatawa.py",
            "--input",
            str(scraped),
            "--output",
            str(drafts),
            "--limit",
            str(args.limit),
        ]
    )
    print(f"pipeline complete scraped={scraped} drafts={drafts}")


if __name__ == "__main__":
    main()
