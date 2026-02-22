#!/usr/bin/env python3
"""Scrape IslamQA.org posts via sitemap into structured JSONL."""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

SITEMAP_INDEX = "https://islamqa.org/sitemap_index.xml"
HEADERS = {
    "User-Agent": "QuranQA-ResearchBot/0.1 (+quranqa.org; educational use)",
}

QUESTION_SPLIT_MARKERS = [
    r"\bQuestion\b[:\s]*",
    r"السؤال[:\s]*",
]

ANSWER_SPLIT_MARKERS = [
    r"\bAnswer\b[:\s]*",
    r"\bThe answer is\b[:\s]*",
    r"الجواب[:\s]*",
]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def fetch_text(session: requests.Session, url: str, timeout: float = 30.0) -> str:
    for attempt in range(4):
        try:
            res = session.get(url, headers=HEADERS, timeout=timeout)
            res.raise_for_status()
            return res.text
        except Exception:
            if attempt == 3:
                raise
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"unreachable fetch loop: {url}")


def parse_xml_locs(xml_text: str) -> list[str]:
    soup = BeautifulSoup(xml_text, "xml")
    return [node.get_text(strip=True) for node in soup.find_all("loc")]


def extract_question_answer(raw: str) -> tuple[str, str]:
    text = normalize_space(raw)
    if not text:
        return "", ""

    for marker in ANSWER_SPLIT_MARKERS:
        m = re.search(marker, text, flags=re.IGNORECASE)
        if m:
            q = normalize_space(text[: m.start()])
            a = normalize_space(text[m.end() :])
            for q_marker in QUESTION_SPLIT_MARKERS:
                q = re.sub(q_marker, "", q, flags=re.IGNORECASE).strip()
            return q, a

    return text, ""


@dataclass
class ScrapedEntry:
    url: str
    id: Optional[int]
    madhhab: str
    source: str
    title: str
    question: str
    source_answer: str
    raw_text: str
    scraped_at_unix: int

    def as_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)


def parse_url_meta(url: str) -> tuple[Optional[int], str, str]:
    parts = [p for p in urlparse(url).path.split("/") if p]
    post_id = None
    madhhab = ""
    source = ""
    if len(parts) >= 4:
        madhhab = parts[0]
        source = parts[1]
        try:
            post_id = int(parts[2])
        except Exception:
            post_id = None
    return post_id, madhhab, source


def scrape_one(session: requests.Session, url: str) -> Optional[ScrapedEntry]:
    try:
        html = fetch_text(session, url)
    except Exception:
        return None
    soup = BeautifulSoup(html, "html.parser")

    title_node = soup.select_one("h1") or soup.select_one(".entry-title")
    content_node = soup.select_one(".entry-content") or soup.select_one(".post-content")

    title = normalize_space(title_node.get_text(" ", strip=True)) if title_node else ""
    raw_text = normalize_space(content_node.get_text(" ", strip=True)) if content_node else ""
    if not title and not raw_text:
        return None

    question, source_answer = extract_question_answer(raw_text)
    post_id, madhhab, source = parse_url_meta(url)

    return ScrapedEntry(
        url=url,
        id=post_id,
        madhhab=madhhab,
        source=source,
        title=title,
        question=question,
        source_answer=source_answer,
        raw_text=raw_text,
        scraped_at_unix=int(time.time()),
    )


def load_existing_urls(path: Path) -> set[str]:
    if not path.exists():
        return set()
    seen = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                u = obj.get("url")
                if u:
                    seen.add(u)
            except json.JSONDecodeError:
                continue
    return seen


def iter_post_urls(session: requests.Session) -> Iterable[str]:
    idx_xml = fetch_text(session, SITEMAP_INDEX)
    sitemaps = parse_xml_locs(idx_xml)
    post_maps = [u for u in sitemaps if "sitemap-posts.xml" in u]
    for sm_url in post_maps:
        try:
            sm_xml = fetch_text(session, sm_url)
        except Exception:
            continue
        for loc in parse_xml_locs(sm_xml):
            if not loc.startswith("https://islamqa.org/"):
                continue
            if "islamqa.info" in loc:
                continue
            yield loc


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape IslamQA.org into JSONL")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    parser.add_argument("--limit", type=int, default=2000, help="Max records")
    parser.add_argument("--workers", type=int, default=12, help="Parallel workers")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    seen_urls = load_existing_urls(output)
    target = args.limit

    candidate_urls = []
    for u in iter_post_urls(session):
        if u in seen_urls:
            continue
        candidate_urls.append(u)
        if len(candidate_urls) >= target * 2:
            break

    written = 0
    with output.open("a", encoding="utf-8") as out, cf.ThreadPoolExecutor(
        max_workers=max(1, args.workers)
    ) as pool:
        futures = [pool.submit(scrape_one, session, u) for u in candidate_urls]
        for fut in cf.as_completed(futures):
            item = fut.result()
            if item is None:
                continue
            out.write(item.as_json() + "\n")
            written += 1
            if written % 100 == 0:
                out.flush()
                print(f"scraped={written}")
            if written >= target:
                break

    print(f"done wrote={written} output={output}")


if __name__ == "__main__":
    main()
