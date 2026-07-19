# Failure #8 — State Drift

> The invoice said $120050. The math was 1200 + 50. Nothing crashed.

## What it looks like in production

A shared state dict threads through your pipeline. One step writes a number as a string — fresh off an external API — and three steps later `+` concatenates instead of adding. No exception, no log line, just a wrong number moving confidently toward a customer. String-typed totals, swapped keys, stale fields: state corrupts quietly between steps, and by the time you see it, you can't tell which step did it.

## The lesson

**State needs a contract, and every step's output gets validated against it.**

The step that corrupts state should be the step named in the stack trace — not a mystery you reconstruct three days later.

## Files in this folder

- `broken.py` — mutable dict, no validation; concatenates its way to a $120050 invoice.
- `fixed.py` — state schema, per-step validation, copies instead of shared mutation, audit trail.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # invoice total: '120050'   (should be 1250)
python fixed.py    # invoice total: 1250, with a per-step audit trail
```

## The fix in one sentence

Define a typed schema for pipeline state, validate after every step, hand each step a copy — and coerce external data at the boundary where it enters.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
