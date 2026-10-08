# Failure #14: Rubber-Stamp Verifier

> The worker said "verified." The verifier believed it. The invoice total was $4.00 short.

## What it looks like in production

A second agent exists to check the first one's work, so the pipeline looks safe. But the checker reads the worker's own report and approves anything confident. It recomputes nothing, so it can only agree. Every wrong answer leaves with a stamp on it.

## The lesson

**A verifier must produce its own evidence from the original inputs. It never accepts the worker's claim, and it never approves what it can't check.**

## Files in this folder

- `broken.py`: approves on the worker's self-report.
- `fixed.py`: recomputes from the inputs, records the evidence, and refuses when it has no independent check.
- `tests/`: pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # approved=True on a wrong total
python fixed.py    # approved=False, with the recomputed number
```

## The fix in one sentence

Recompute from the inputs with separate code, compare, keep the evidence, and treat "no check available" as a rejection.

## Read the lesson

Full written walkthrough: [Failure 14 in *The Agent Autopsy* series](https://menokoog.github.io/agent-autopsy/failures/14-rubber-stamp-verifier/).
