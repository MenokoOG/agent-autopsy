# Failure #1 — The Runaway Loop

> An agent calls itself forever, burns through tokens overnight, and you wake up to a $400 bill.

## What it looks like in production

You ship an agent that decides when it's done. It works in testing — three iterations, finishes cleanly. In prod, an edge case hits: the agent's "am I done?" check returns false every time. It loops. Nothing stops it. The cost meter spins until your rate limit or your wallet trips.

## The lesson

**Never let an agent be the only thing deciding when to stop.**

Stop conditions belong outside the agent's judgment. Iteration caps, token budgets, wall-clock timeouts — all of these are non-negotiable for any loop that calls a model.

## Files in this folder

- `broken.py` — runnable agent with no stop guard. Will spin until your API key cuts out.
- `fixed.py` — same agent, three layers of stop conditions added.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
# WARNING: broken.py will burn tokens. Cap your API key spend before running.
python broken.py

# This one is safe.
python fixed.py
```

## The fix in one sentence

Wrap every agent loop in a `for _ in range(MAX_STEPS)` with a token budget check and a hard timeout — and log every step so you can see what it was thinking when you cut it off.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
