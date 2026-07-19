# Failure #9 — The Amnesia Bug

> The batch crashed at item 3. The retry started at item 1. Two customers got the email twice.

## What it looks like in production

Your agent works through a queue — emails, charges, API calls. A network blip kills it mid-batch. The scheduler restarts it, and it remembers nothing: every side effect completed before the crash happens again. Duplicate welcome emails are embarrassing; duplicate charges are refund tickets and trust damage.

## The lesson

**Completed work must be recorded durably before the next item starts.**

An agent that can't prove what it finished will eventually redo it — against real users.

## Files in this folder

- `broken.py` — no work log; crash + retry = duplicate side effects.
- `fixed.py` — append-only checkpoint file; restart skips finished items, each effect happens exactly once.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # users emailed twice: {'ana@...': 2, 'bo@...': 2, ...}
python fixed.py    # users emailed twice: none
```

## The fix in one sentence

Write each completed item to a durable checkpoint before moving on, and consult the checkpoint on startup — crash-and-retry then costs you at most one repeated attempt, never a repeated side effect.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
