# Failure #4 — Tool Hallucination

> The model asked for `database_query`. You never built a `database_query`. KeyError at 2 a.m.

## What it looks like in production

Your agent has two tools. The model, pattern-matching on what an agent *should* have, requests a third one that sounds plausible — `database_query`, `send_email`, `get_user_profile`. Your dispatch code does `TOOLS[name](**args)` and crashes on the lookup. Or worse: a fuzzy-match router runs the *wrong* real tool instead.

## The lesson

**The tool registry is the source of truth — the model's imagination is not.**

Validate every tool request against the registry before executing. On a miss, tell the model exactly what exists and let it retry, bounded.

## Files in this folder

- `broken.py` — executes whatever tool name the model emits. Crashes on the hallucination.
- `fixed.py` — registry validation, corrective feedback, three bounded retries, loud failure.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # KeyError: 'database_query'
python fixed.py    # corrected to a real tool on attempt 2
```

## The fix in one sentence

Check `name in tools` before dispatch, feed the real tool list back to the model on a miss, cap the retries, and raise loudly if it never picks a valid one.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
