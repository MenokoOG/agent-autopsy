# Failure #7 — Context Collapse

> Thirty steps in, the agent forgot what it was hired to do — because the trimming code threw the goal away.

## What it looks like in production

Long-running task, context window fills, and your trimming code keeps "the most recent N messages." Message 0 — the actual mission, with its "do NOT touch the auth service" warning — is the first thing cut. The agent keeps working diligently on whatever the recent chatter mentions. That's how a billing migration becomes an auth refactor.

## The lesson

**Pin the goal. Trim the middle, never the ends.**

A model only knows what's in its context. Detail is expendable; the mission is not.

## Files in this folder

- `broken.py` — keep-last-N trimming drops the goal; the agent drifts to a different task.
- `fixed.py` — goal pinned, middle summarized to a marker, recent tail kept.
- `tests/` — pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # goal still in context: False — and it's "refactoring auth"
python fixed.py    # goal still in context: True — still on the migration
```

## The fix in one sentence

Build context as `[pinned goal] + [summary of the trimmed middle] + [recent messages]` so no amount of trimming can ever evict the mission.

## Read the lesson

Full written walkthrough: *The Agent Autopsy* series on freeCodeCamp (coming soon).
