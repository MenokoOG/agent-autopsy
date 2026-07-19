# Failure #11 — The Confident Liar

> Search returned nothing. The agent reported "$4.21 billion, up 12%" with a citation it invented.

## What it looks like in production

The data isn't there — the search came back empty, the API returned nothing. But the model was asked for a number, and models abhor a vacuum: it produces a specific, plausible, wrong figure, often with a fabricated source attached. The user can't tell grounded from invented. That's the worst part — the lie looks exactly like the truth.

## The lesson

**Grounding is enforced in code, not requested in the prompt.**

No evidence, no factual answer — computed by an `if` statement, not left to the model's conscience. Claims with no citation get rejected on the way out.

## Files in this folder

- `broken.py` — empty evidence, confident fabricated answer, shipped.
- `fixed.py` — evidence gate before the model is called, citation check after; "I could not verify this" is a first-class answer.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # $4.21 billion (invented)
python fixed.py    # "I could not verify this..." (honest)
```

## The fix in one sentence

Gate the answer on evidence existing, require every specific claim to cite an evidence ID, and return an explicit "can't verify" when either gate fails — an honest unknown beats a confident fiction.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
