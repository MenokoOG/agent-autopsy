# Failure #6 — Wrong Tool Pick

> The question was arithmetic. The agent googled it and returned a 2019 forum guess.

## What it looks like in production

"What is 12.5% of 3,847?" Your router sees "What is..." and reaches for web search — the hammer it reaches for on everything. Search returns a stale, confidently wrong snippet, and the agent passes it along. The calculator that would have nailed it in microseconds never gets called.

## The lesson

**Route on what the task needs, not on what the question looks like.**

Exact computation needs a calculator. Fresh external facts need search. A deterministic classifier for the easy cases beats a vibes-based default every time.

## Files in this folder

- `broken.py` — routes everything to web search. Returns the stale forum answer.
- `fixed.py` — extracts the math, routes computation to the calculator, keeps search for facts.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # "about 480" (wrong)
python fixed.py    # 480.875 (exact)
```

## The fix in one sentence

Classify the task's need first — computable expression → calculator, external fact → search — and only fall back to model judgment when the deterministic rules don't match.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
