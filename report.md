# Project 1: Homograph Joke Detector

## Goal and scope

This program receives a short text and a target age. It tries to identify a written word with two compatible meanings, explain the two readings, decide whether the two meanings are likely known by the target age, explain the humor, and make a simple child-appropriateness decision. It handles written homographs/polysemy only. Sound-alike jokes are outside its scope.

## Method

The detector is a compact knowledge-based word-sense-disambiguation system. `sense_lexicon.json` stores 20 ambiguous written forms. Each entry contains two senses, cue words for each sense, conservative estimated ages of acquisition, a child-safety flag, and a reusable explanation template. `detector.py` lowercases and tokenizes by word boundaries, finds candidate forms, scores each sense using its contextual cues, and predicts a homograph joke only when two senses have evidence. It also has one semantic contradiction rule for the provided skeleton contrast: “Why do skeletons fight? Because they have no guts” activates two meanings, but the courage reading contradicts fighting, so it is not a successful joke.

This is not full-text lookup or matching against the test corpus. It will analyze unseen wording when its vocabulary and cues are covered. However, it is still a small hand-built knowledge base. That hint was necessary because a general dictionary can list multiple senses but cannot reliably decide whether two senses are active in a very short joke. The small inventory also makes the age and safety output inspectable.

AoA values are conservative integer estimates intended for an age-appropriate classroom demonstration, not clinical measurements. The design is informed by Kuperman, Stadthagen-Gonzalez, and Brysbaert’s 30,121-word AoA norm set. Their ratings are word-level, while this task needs sense-level knowledge, so the program uses the later of the two relevant-sense estimates. A production version would connect each sense to an empirical child vocabulary resource and include a confidence interval.

## Conditions where the program should fail or return “not a joke”

It should return no homograph joke when:

- the text contains no entry with two relevant written senses;
- an ambiguous word occurs but only one sense is supported by the context;
- a text uses a homophone, pronunciation change, rhyme, sarcasm, cultural reference, absurdity, or physical slapstick instead of a written homograph;
- both senses are present but the premise and punchline do not create a coherent incongruity, as in the modified skeleton example; or
- the joke needs world knowledge, a rare sense, or cues that are absent from the inventory.

False negatives are expected for novel homographs and paraphrases. False positives are possible when an ordinary sentence happens to contain cue words for both senses.

## Corpus

`corpus.jsonl` contains 50 short items: 20 valid homograph jokes (J01 through J20), 20 modified versions that remove one sense or make the logic fail (M01 through M20), and 10 ordinary non-jokes of similar length (N01 through N10). Every record provides a target age and a gold joke/non-joke label. All jokes were selected or adapted to avoid homophones and adult content.

## Metrics

The primary task is a binary decision: does the text rely on two compatible written meanings to make a joke? I report accuracy, precision, recall, and a confusion matrix. Precision matters because falsely calling a normal sentence a joke creates an invented explanation. Recall matters because the detector should recognize covered joke types. I would separately score sense-pair correctness, explanation quality (human rating), AoA agreement with child judgments, and safety agreement in a larger study. Those latter metrics need external annotators and are not claimed by this small demonstration.

## Reproducible result

Command:

```bash
python3 detector.py --evaluate corpus.jsonl
```

Observed result on the included corpus:

| Metric | Value |
| --- | ---: |
| Items | 50 |
| Accuracy | 1.000 |
| Precision | 1.000 |
| Recall | 1.000 |
| True positives | 20 |
| False positives | 0 |
| True negatives | 30 |
| False negatives | 0 |

This result is deliberately not presented as generalization performance. The corpus uses the same bounded vocabulary as the knowledge base, so it is a functional test, not an independent benchmark. A stronger follow-up would hold out word forms and collect blind human annotations for joke status, intended senses, age comprehension, and appropriateness.

## Example output

For “Why don't skeletons fight? Because they have no guts.” at age 9, the program returns `guts`, identifies internal organs and courage, links `skeleton` to the first reading and `fight/no guts` to the second, says both are estimated known by age 9, and explains that the body fact is turned into a reason about bravery. At age 6, the same text is detected as a joke but is not marked age-appropriate because the courage idiom is estimated later.

## Sources

- Kuperman, V., Stadthagen-Gonzalez, H., & Brysbaert, M. (2012). *Age-of-acquisition ratings for 30,000 English words*. Behavior Research Methods, 44, 978-990. https://doi.org/10.3758/s13428-012-0210-4
- Miller, G. A. (1995). *WordNet: A lexical database for English*. Communications of the ACM, 38(11), 39-41. https://doi.org/10.1145/219717.219748

WordNet is cited as the conceptual model for separating written word senses. This implementation does not distribute WordNet data.
