#!/usr/bin/env python3
"""Generate first-pass neo-Mutazili, Quran-centric draft fatawa."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path


PRINCIPLES = [
    "tawhid (divine unity) and rejection of superstition",
    "adl (moral justice) and human accountability",
    "aql (reason) as a tool to apply revelation",
    "maslaha (public welfare) and harm-reduction",
    "Quran-first legal framing before secondary authorities",
]

PROFILE_DIRECTIVES = {
    "riba-finance": [
        "Riba is treated as a major structural injustice because compounding debt concentrates wealth and transfers risk downward.",
        "Avoidance of riba is framed as moral struggle (jihad al-nafs and social justice commitment).",
        "Preferred alternatives include equity-aligned contracts and asset-linked structures such as transparent murabaha or share buyback style participation models.",
    ],
    "worship-ritual": [
        "Use Ibn Masud's tashahhud formulation with ala Nabi wording and avoid language that appears to invoke a deceased person.",
        "Use shortened tashahhud in the second rakat.",
        "Preface prayer with Subhanaka Rabana from Quran 10:10 framing, and close with Alhamdulillah.",
    ],
    "marriage-family": [
        "Mutah is treated as halal in this profile.",
        "Secret second marriage is rejected as unfair dealing; fairness and disclosure are required.",
        "For non-Muslims in exclusive boyfriend-girlfriend relationships, do not flatten all cases into fornication; apply urfi social context.",
        "Integrate the ethical warning associated with Mark 10 transmission attributed to Jesus: do not expel spouses from homes or impose cruel divorce.",
        "Prioritize mutual-consent divorce pathways and release with ihsan when continuation becomes harmful.",
    ],
    "gambling": [
        "Maisir and pure chance betting remain impermissible.",
        "Positive expected value trading with disciplined risk controls is not automatically gambling.",
        "Options and algorithmic strategies can be mubah when tied to real analysis, bounded risk, and non-exploitative intent.",
    ],
    "diet-halal": [
        "Diet strictness is treated as mustahabb in Jafari style and mubah latitude in Hanafi style where text allows.",
        "Avoid expanding haram categories beyond clear Quranic prohibitions without necessity.",
    ],
    "intoxicants": [
        "Alcohol remains haram.",
        "Cannabis/weed is treated as makruh in this profile unless concrete harm/intoxication level escalates ruling.",
        "Ibn Sina style medical-rational framing is used for substance evaluation.",
    ],
    "medical-necessity": [
        "Medical necessity receives broad facilitation when harm reduction is credible.",
        "Use inductive reasoning for transformation-of-nature questions in medicine and bioethics.",
        "Gender transition care is treated with cautious openness under clinical necessity, aligning with flexible contemporary Shii precedents.",
    ],
    "sectarian-ethics": [
        "Reject takfir-first polemics and prohibit sectarian humiliation, abuse, and dehumanization.",
        "Treat disagreement between Sunni, Twelver, Zaydi, and Quranist trajectories through adab, evidence, and justice.",
        "Affirm that moral rank is by taqwa and justice, not inherited sect label.",
    ],
    "mutazili-lineage": [
        "Present neo-Mutazili thought as an intersectional rationalist stream that can engage early Shii currents, including Kaysani-linked narratives, without collapsing into identity warfare.",
        "Use historical claims as probabilistic historiography, not a weapon for excommunication.",
        "Center shared Quranic ethics over factional triumphalism.",
    ],
    "ai-ethics": [
        "Beneficial AI use for education, justice, anti-fraud, and safety is mubah and can rise toward communal obligation when harms are high.",
        "AI safety, alignment, robustness, and misuse prevention qualify as jihad in the nonviolent sense of striving to reduce harm and protect society.",
        "Ban oppressive or deceptive use: surveillance abuse, targeted fraud, deepfake slander, and autonomous harm.",
    ],
}


TOPIC_RULES = [
    {
        "name": "riba-finance",
        "keywords": [
            "interest",
            "riba",
            "bank",
            "mortgage",
            "loan",
            "credit card",
            "apr",
        ],
        "default_verdict": "impermissible-or-needs-ethical-alternative",
        "verses": ["2:275-279", "3:130", "4:29"],
        "reason": "Exploitative gain and unjust enrichment conflict with Quranic justice.",
    },
    {
        "name": "intoxicants",
        "keywords": ["alcohol", "wine", "beer", "intoxic", "drunk", "khamr"],
        "default_verdict": "impermissible",
        "verses": ["5:90-91", "2:219", "16:67"],
        "reason": "Intoxication impairs reason and social responsibility.",
    },
    {
        "name": "gambling",
        "keywords": ["gambl", "bet", "casino", "lottery", "poker"],
        "default_verdict": "impermissible-with-trading-exception",
        "verses": ["5:90-91", "2:219", "4:29"],
        "reason": "Gambling causes social harm and unearned transfer of wealth.",
    },
    {
        "name": "diet-halal",
        "keywords": ["gelatin", "pork", "zabiha", "food", "ingredient", "slaughter"],
        "default_verdict": "contextual",
        "verses": ["2:168", "2:173", "5:3", "6:145"],
        "reason": "Food law should track explicit Quranic prohibitions and avoid excess rigidity.",
    },
    {
        "name": "marriage-family",
        "keywords": [
            "marry",
            "marriage",
            "divorce",
            "nikah",
            "wife",
            "husband",
            "foster",
            "sibling",
            "rada",
            "custody",
        ],
        "default_verdict": "contextual",
        "verses": ["4:1", "4:19", "30:21", "65:1-2"],
        "reason": "Family rulings should preserve dignity, consent, and fairness.",
    },
    {
        "name": "worship-ritual",
        "keywords": ["prayer", "salah", "wudu", "fast", "ramadan", "zakat", "hajj"],
        "default_verdict": "obligation-with-facilitation",
        "verses": ["2:183-185", "2:286", "4:103", "10:10", "22:78"],
        "reason": "Worship remains obligatory while Quranic ease principles apply in hardship.",
    },
    {
        "name": "medical-necessity",
        "keywords": ["medicine", "medical", "treatment", "insulin", "surgery", "capsule"],
        "default_verdict": "permissible-by-necessity",
        "verses": ["2:173", "4:29", "5:32", "6:119"],
        "reason": "Necessity and preservation of life permit restricted exceptions.",
    },
    {
        "name": "sectarian-ethics",
        "keywords": [
            "sect",
            "sunni",
            "shia",
            "twelver",
            "zaydi",
            "quranist",
            "anti-sectarian",
            "takfir",
            "madhhab",
        ],
        "default_verdict": "anti-sectarian-obligation",
        "verses": ["3:103", "6:159", "49:10", "49:13"],
        "reason": "Factional hatred violates unity, justice, and fraternity ethics.",
    },
    {
        "name": "mutazili-lineage",
        "keywords": ["mutazili", "kaysani", "intersection", "lineage", "descended"],
        "default_verdict": "historical-claim-with-adab",
        "verses": ["17:36", "49:6", "39:18"],
        "reason": "Historical claims require evidence discipline and ethical restraint.",
    },
    {
        "name": "ai-ethics",
        "keywords": [
            "ai",
            "artificial intelligence",
            "alignment",
            "safety research",
            "llm",
            "deepfake",
            "misinformation",
            "automation",
            "model",
        ],
        "default_verdict": "mubah-to-fard-kifaya-by-harm-profile",
        "verses": ["5:2", "16:90", "17:36", "99:7-8"],
        "reason": "Tools inherit rulings from use: benefit is encouraged, preventable harm is prohibited.",
    },
]

EXCEPTIONS = [
    {
        "keywords": ["necessity", "darura", "emergency", "life-threatening"],
        "note": "If genuine necessity is established, a narrow temporary exception may apply.",
        "verses": ["2:173", "6:119"],
    },
    {
        "keywords": ["coerc", "forced", "duress"],
        "note": "Moral liability is reduced under coercion; reassess agency and alternatives.",
        "verses": ["16:106"],
    },
]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def pick_topic(text: str) -> dict:
    best = None
    best_score = -1
    for rule in TOPIC_RULES:
        score = sum(1 for kw in rule["keywords"] if kw in text)
        if score > best_score:
            best = rule
            best_score = score
    return best or TOPIC_RULES[0]


def find_exception_notes(text: str) -> tuple[list[str], list[str]]:
    notes = []
    verses = []
    for ex in EXCEPTIONS:
        if any(kw in text for kw in ex["keywords"]):
            notes.append(ex["note"])
            verses.extend(ex["verses"])
    return notes, verses


def generate_draft(entry: dict) -> dict:
    text = normalize(
        " ".join(
            [
                entry.get("title", ""),
                entry.get("question", ""),
                entry.get("raw_text", ""),
            ]
        )
    )
    topic = pick_topic(text)
    extra_notes, extra_verses = find_exception_notes(text)
    verses = sorted(set(topic["verses"] + extra_verses))

    question_summary = entry.get("question") or entry.get("title") or "No question text extracted."
    if len(question_summary) > 300:
        question_summary = question_summary[:300].rstrip() + "..."

    answer_lines = [
        f"Preliminary verdict: {topic['default_verdict']}.",
        f"Quran-centric rationale: {topic['reason']}",
        "Method: apply revelation through reason, justice, and public welfare.",
    ]
    answer_lines.extend(PROFILE_DIRECTIVES.get(topic["name"], []))
    if extra_notes:
        answer_lines.extend(extra_notes)
    answer_lines.append(
        "Draft stance: allow what sustains justice and human dignity; restrict what creates injustice, intoxication, or exploitation."
    )
    answer_lines.append(
        "This is a machine-generated draft for review and refinement by the MutaziliFatawa skill."
    )

    return {
        "url": entry.get("url"),
        "title": entry.get("title"),
        "question_summary": question_summary,
        "topic": topic["name"],
        "neo_mutazili_principles": PRINCIPLES,
        "quran_references": verses,
        "draft_fatwa_text": " ".join(answer_lines),
        "generated_at_unix": int(time.time()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate neo-Mutazili drafts from scraped entries")
    parser.add_argument("--input", required=True, help="Input JSONL of scraped IslamQA entries")
    parser.add_argument("--output", required=True, help="Output JSONL of draft fatawa")
    parser.add_argument("--limit", type=int, default=2000, help="Max rows to process")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = 0
    with in_path.open("r", encoding="utf-8") as src, out_path.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            entry = json.loads(line)
            draft = generate_draft(entry)
            dst.write(json.dumps(draft, ensure_ascii=False) + "\n")
            rows += 1
            if rows >= args.limit:
                break

    print(f"done generated={rows} output={out_path}")


if __name__ == "__main__":
    main()
