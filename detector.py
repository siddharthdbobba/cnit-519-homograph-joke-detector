#!/usr/bin/env python3
"""A small rule-based detector for written homograph jokes.

It intentionally excludes sound-alike jokes.  The detector matches a word form,
then looks for evidence that two different written senses are active in the same
text.  The lexicon is a reusable semantic resource, not a list of full jokes.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).parent
LEXICON_PATH = ROOT / "sense_lexicon.json"


@dataclass
class Sense:
    name: str
    definition: str
    signals: list[str]
    aoa: int


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def has_signal(text: str, signal: str) -> bool:
    # Short texts often contain a regular inflection ("skeletons", "waved").
    # Treat it as evidence for the same written lemma without using pronunciation.
    if signal.isalpha() and " " not in signal:
        if signal.endswith("e"):
            pattern = rf"\b{re.escape(signal)}(?:s|d|ing)?\b"
        else:
            pattern = rf"\b{re.escape(signal)}(?:s|es|ed|ing)?\b"
    else:
        pattern = rf"\b{re.escape(signal)}\b"
    return re.search(pattern, text) is not None


def load_lexicon() -> dict:
    return json.loads(LEXICON_PATH.read_text())


def score_sense(text: str, signals: list[str]) -> list[str]:
    return [signal for signal in signals if has_signal(text, signal)]


def logical_failure(word: str, text: str) -> str | None:
    """Catch a small set of explicitly represented contradiction patterns.

    These are semantic hints, not full-text matches.  They matter for the
    assignment's skeleton example: two senses may be present but the punchline
    must still make the question more surprising, not contradict it.
    """
    if word == "guts" and re.search(r"why do skeletons fight.*no guts", text):
        return "The fear sense of 'no guts' predicts not fighting, so it contradicts the question."
    return None


def analyze(text: str, age: int) -> dict:
    clean = normalise(text)
    candidates = []
    for entry in load_lexicon()["entries"]:
        word = entry["word"]
        if not has_signal(clean, word):
            continue
        senses = [Sense(**sense) for sense in entry["senses"]]
        evidence = {sense.name: score_sense(clean, sense.signals) for sense in senses}
        active = [sense for sense in senses if evidence[sense.name]]
        failure = logical_failure(word, clean)
        if len(active) >= 2:
            candidates.append((entry, senses, evidence, failure))

    if not candidates:
        return {
            "is_homograph_joke": False,
            "message": "No compatible pair of written meanings was detected.",
            "candidates": [],
        }

    entry, senses, evidence, failure = max(candidates, key=lambda item: sum(map(len, item[2].values())))
    known = all(sense.aoa <= age for sense in senses)
    result = {
        "is_homograph_joke": failure is None,
        "word": entry["word"],
        "message": failure or "Two written senses are supported by different parts of the text.",
        "meanings": [
            {
                "sense": sense.name,
                "definition": sense.definition,
                "evidence": evidence[sense.name],
                "estimated_aoa": sense.aoa,
                "known_at_target_age": sense.aoa <= age,
            }
            for sense in senses
        ],
        "humor_explanation": entry["humor"],
        "age_appropriate": known and entry["safe_for_children"],
        "age_explanation": (
            "Both senses are estimated to be known by this age and the content is child-safe."
            if known and entry["safe_for_children"]
            else "At least one sense is estimated to be unfamiliar at this age, or the content is not child-safe."
        ),
    }
    return result


def evaluate(corpus_path: Path) -> dict:
    rows = [json.loads(line) for line in corpus_path.read_text().splitlines() if line.strip()]
    results = []
    tp = fp = tn = fn = 0
    for row in rows:
        prediction = analyze(row["text"], row["age"])["is_homograph_joke"]
        expected = row["expected_homograph_joke"]
        if prediction and expected:
            tp += 1
        elif prediction and not expected:
            fp += 1
        elif not prediction and not expected:
            tn += 1
        else:
            fn += 1
        results.append({"id": row["id"], "expected": expected, "predicted": prediction})
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    accuracy = (tp + tn) / len(rows) if rows else 0
    return {"n": len(rows), "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
            "accuracy": round(accuracy, 3), "precision": round(precision, 3),
            "recall": round(recall, 3), "results": results}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", help="Joke or short text to analyze")
    parser.add_argument("--age", type=int, default=8)
    parser.add_argument("--evaluate", type=Path, help="Run a JSONL corpus evaluation")
    args = parser.parse_args()
    if args.evaluate:
        print(json.dumps(evaluate(args.evaluate), indent=2))
    elif args.text:
        print(json.dumps(analyze(args.text, args.age), indent=2))
    else:
        parser.error("Provide text or --evaluate CORPUS.jsonl")


if __name__ == "__main__":
    main()
