# Failure #13: Reasoning-Action Mismatch

> The agent said it would refund $20.00 on A100. The ledger shows $200.00 paid out on A101.

## What it looks like in production

The agent writes a clear explanation of what it is about to do, then calls a tool with different arguments. The explanation goes to the user and the logs. The call goes to the system of record. Nothing compares the two, so a reviewer who reads the log sees a sensible plan while the money moved somewhere else.

## The lesson

**Make the agent declare its intent as structured data, then compare it with the actual call in code. Refuse to run on any difference.**

## Files in this folder

- `broken.py`: shows the user one story and executes another.
- `fixed.py`: field-by-field comparison of declared intent and actual call, with an audit trail.
- `tests/`: pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # says A100, pays out on A101
python fixed.py    # BLOCKED until intent and call agree
```

## The fix in one sentence

Prose can't be checked and a schema can, so require a structured intent, diff it against the call, and block on any mismatch.

## Read the lesson

Full written walkthrough: [Failure 13 in *The Agent Autopsy* series](https://menokoog.github.io/agent-autopsy/failures/13-reasoning-action-mismatch/).
