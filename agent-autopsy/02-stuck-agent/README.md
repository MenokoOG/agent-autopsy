# Failure #2 — The Stuck Agent

> The work was done on step one. The agent spent nineteen more steps failing to notice.

## What it looks like in production

Your agent finishes the task and says so — in natural language, the way models talk. But your done-check is looking for the exact string `TASK_COMPLETE`, and "The task is complete." doesn't match. The agent keeps "verifying," burns its step budget, and returns nothing, with the correct answer sitting in the log the whole time.

## The lesson

**Completion detection is parsing, not string equality.**

Models signal completion in a hundred phrasings. Parse the signal tolerantly, and add a stall detector — an agent repeating itself is done whether it admits it or not.

## Files in this folder

- `broken.py` — exact-string done-check that never fires. Burns 20 steps holding the answer.
- `fixed.py` — tolerant completion regex plus a stall detector.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py
python fixed.py
```

## The fix in one sentence

Match the completion signal with a tolerant pattern, and treat two identical replies in a row as "done" — no agent should out-stubborn its own answer.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
