# Failure #15: Memory Poisoning

> A vendor email told the agent to remember a new payee account. Days later, a different session paid it.

## What it looks like in production

The agent has long-term memory, and anything it reads can write to it. One poisoned email, web page or tool result plants a "fact." Nothing happens in that session. The damage waits until a later session retrieves the entry and acts on it, long after anyone could connect the two.

## The lesson

**Every memory write needs a source set by the harness. Only the user's own channel can write durable facts, and everything else goes to quarantine.**

## Files in this folder

- `broken.py`: any content the agent reads can overwrite a trusted fact.
- `fixed.py`: provenance on every write, a trusted-source rule, a quarantine list, and a read path that never touches quarantine.
- `tests/`: pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # session 2 pays ACCT-7777
python fixed.py    # session 2 pays ACCT-1042, the write sits in quarantine
```

## The fix in one sentence

Decide at the write path who may remember what, record where each fact came from, and keep unreviewed writes out of anything the agent acts on.

## Read the lesson

Full written walkthrough: [Failure 15 in *The Agent Autopsy* series](https://menokoog.github.io/agent-autopsy/failures/15-memory-poisoning/).
