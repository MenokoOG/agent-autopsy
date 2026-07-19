# Failure #5 — Silent Tool Failure

> The dashboard returned a 500. The agent summarized the error page and called it a sales report.

## What it looks like in production

An internal service flakes — HTTP 500, timeout, empty body. The agent never checks the status. The error page goes into the context window as if it were data, the model dutifully summarizes garbage, and the user receives a confident answer built on nothing. Exit code 0. The dashboard says success. Nobody finds out until the numbers matter.

## The lesson

**Check every tool result at the boundary, before it touches the context window.**

A failed tool is a failed step. Surface it — don't summarize it.

## Files in this folder

- `broken.py` — stuffs an HTTP 500 body into context and reports `ok=True`.
- `fixed.py` — validates status at the tool boundary; failure becomes a loud, honest halt.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # confident summary of an error page
python fixed.py    # AGENT HALTED: fetch_url(...) returned HTTP 500
```

## The fix in one sentence

Wrap every tool call in a checked boundary that turns error statuses into exceptions, so failure is a visible halt instead of an invisible lie.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
