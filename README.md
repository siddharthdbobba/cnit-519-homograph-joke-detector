# Homograph Joke Detector

A standard-library Python prototype for CNIT 519 Project 1. It accepts a short text and an age, identifies compatible written meanings, estimates whether both meanings are familiar at that age, explains the humor, and returns a child-safety decision.

It only analyzes written homographs or polysemous written forms. It deliberately does not accept homophone-based jokes such as “wine/whine” or “two/tired.”

## Run

```bash
python3 detector.py "Why don't skeletons fight? Because they have no guts." --age 9
python3 detector.py --evaluate corpus.jsonl
```

The supplied corpus has 50 texts: 20 homograph jokes, 20 modified versions that are no longer jokes, and 10 similarly short non-jokes.

See `report.md` for method, failure conditions, results, metrics, sources, and limitations.
