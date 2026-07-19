# Failure #12 — No Human Brake

> The agent decided the records looked stale. The customer table was empty before anyone knew a decision had been made.

## What it looks like in production

Every action the agent decides on, it executes — same code path for archiving a report and deleting a customer table. No classification of what can be undone, no checkpoint before the point of no return, no human anywhere in the loop. The plan looked reasonable. It usually does.

## The lesson

**Irreversible actions stop and wait for a human. No approver, no execution.**

Humans keep final authority over consequential decisions — LAHA isn't a slogan here, it's a code path. Agents earn trust by being auditable, not by being autonomous.

## Files in this folder

- `broken.py` — executes deletes the moment the agent decides them.
- `fixed.py` — declared irreversible-action set, hard approval gate with impact context, full audit trail.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # customers table: []
python fixed.py    # HELD FOR APPROVAL — table intact until a human says yes
```

## The fix in one sentence

Declare which actions are irreversible, route them through an approval gate that shows the human exactly what will be destroyed, and audit every decision — auto-run only what you can undo.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
