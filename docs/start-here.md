---
title: Start here
permalink: /start-here/
---

# Start here

Most agent tutorials show you how to build one. This series shows you what breaks after you do.

The demo works. Production doesn't. The agent loops, trusts a broken tool, forgets its goal, or deletes something nobody approved. Each article in this series takes one of those failures apart, shows the bug in runnable code, and fixes it with a change small enough to read in one sitting.

## What you need

- Python 3.10 or newer
- `git`
- Nothing else. No API key is required.

Every `broken.py` and `fixed.py` ships with a mock model. The mock reproduces the failure on purpose, so you can watch it happen for free. If you set `ANTHROPIC_API_KEY`, the same files call a real model instead. The repo's code uses `claude-sonnet-4-5` in that path.

## Run it

```bash
git clone https://github.com/MenokoOG/agent-autopsy.git
cd agent-autopsy
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

On the repo's current state, that runs 87 tests across the 17 folders. They all pass.

Then pick a failure and run both versions:

```bash
cd 02-stuck-agent
python broken.py
python fixed.py
```

One warning. `01-runaway-loop/broken.py` loops until you press Ctrl+C. In mock mode that costs nothing. With a real key set, it spends tokens. Cap your spend first, or leave the key unset.

## How each article works

Every article follows the same order, so you can skim a familiar shape:

1. **The scenario.** What it looks like when it hits production.
2. **The bug.** The exact lines in `broken.py` and why they fail.
3. **The fix.** The exact lines in `fixed.py` and what each one buys you.
4. **The proof.** Which tests pin the fix in place.
5. **Where the fix stops.** The cases it still doesn't cover. Every fix here has limits, and I'd rather you know them now.
6. **The takeaway.** One sentence to carry into code review.

## Four things to know first

**The models here are mocks.** A mock can only show a failure shape. It can't tell you how often your real model will hit it. Treat each case as a pattern to look for in your logs, not a measurement.

**The fixes are small on purpose.** They're teaching code. A production version of the stall detector or the egress scan needs more than twenty lines. The articles say where.

**The calculator is a toy.** Cases 4 and 6 include a small calculator that parses expressions with Python's `ast` module and allows only numbers and `+ - * / %`. It never calls `eval`. It's enough for the demos, and you should extend its whitelist deliberately if you borrow it.

**Humans keep the final say.** The repo follows a principle I call LAHA, Love All Humans Always. In practice it means every failure here has a human cost: money wasted, trust broken, a decision made without consent. The last case in the series makes that a code path.

## Order

You can read the failures in any order. They're grouped, though, and the loop cases build on each other. If you only have time for three, read [1]({{ '/failures/01-runaway-loop/' | relative_url }}), [5]({{ '/failures/05-silent-tool-failure/' | relative_url }}) and [10]({{ '/failures/10-prompt-injection/' | relative_url }}). Then finish with the [field checklist]({{ '/field-checklist/' | relative_url }}).

[Begin with failure 1: the runaway loop &rarr;]({{ '/failures/01-runaway-loop/' | relative_url }})
