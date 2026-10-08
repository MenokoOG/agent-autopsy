# Failure #17: Limit in the Prompt

> The prompt said refunds stop at $50. The customer asked for $120, and the agent paid it.

## What it looks like in production

A rule that matters, such as a spending cap, a data boundary or a permission, lives only as a sentence in the system prompt. Under pressure from a persistent user or a long conversation, the model gives in or loses track of it. The tool behind it has no check of its own, so it does exactly what it's told.

## The lesson

**A prompt is a request. Code is a guarantee. Put every limit you can't afford to see broken in the tool, and keep a kill switch that sends the work to people.**

## Files in this folder

- `broken.py`: the $50 limit exists only in `SYSTEM_PROMPT`, and a $120 refund goes through.
- `fixed.py`: the limit lives in the refund tool, counts earlier refunds on the same order, escalates to a human queue and has a kill switch.
- `tests/`: pytest cases that prove the fix holds.

## Try it yourself

```bash
python broken.py   # refunded $120.00
python fixed.py    # ESCALATED, split refunds stop at $40, kill switch works
```

## The fix in one sentence

Enforce the limit in the tool path, count cumulative totals so splitting doesn't evade it, and make disabling the bot a tested, one-step action.

## Read the lesson

Full written walkthrough: [Failure 17 in *The Agent Autopsy* series](https://menokoog.github.io/agent-autopsy/failures/17-limit-in-the-prompt/).
