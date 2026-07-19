# Failure #3 — Confidence Collapse

> Right answer on call one. Twenty calls later it's flip-flopped ten times and ships the wrong one.

## What it looks like in production

Someone adds a "double-check your answer" step for quality. It works — so someone makes it a loop. Now every answer triggers another "are you sure?", the model starts waffling the way models do under repeated challenge, and the agent oscillates between two answers until the step cap trips. You pay 20x the tokens and the final answer depends on loop parity.

## The lesson

**Verification needs a budget, and re-checks need a commit rule.**

One verification pass. If it agrees, commit. If it disagrees, one revision — then commit anyway. Unbounded self-doubt destroys more correct answers than it repairs.

## Files in this folder

- `broken.py` — unbounded "are you sure?" loop. Oscillates until the cap.
- `fixed.py` — verify once, allow one revision, commit, log the decision.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py
python fixed.py
```

## The fix in one sentence

Give verification a hard budget (one re-check, one revision) and a commit rule, and log each phase so you can audit why the agent settled where it did.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
