# Agent Autopsy

**12 ways AI agents fail in production. Each one runnable. Each one fixed.**

This is the open-source companion repo for *The Agent Autopsy: 12 Production Disasters, Diagnosed* — a written lesson series for freeCodeCamp by Lawrence Jefferson II (Menoko OG), CEO/CTO of [classHuman AI](https://classhuman.org).

Most agent courses teach you to build one. This one teaches you what breaks when you do.

---

## Why this exists

If you've shipped an AI agent to production, you already know: the demo works, the prod doesn't. The 12 folders in this repo are the failures we've actually seen — runaway loops that burn tokens overnight, tools that lie silently, agents that fabricate results when they should fail loud.

Every failure here has two files:

- `broken.py` — the bug, runnable, fails the way it does in real systems
- `fixed.py` — the fix, with the lesson in the diff

Read the broken code. Run it. Watch it fail. Then read the fix.

---

## The 12 Failures

### Loop & Control
1. [Runaway Loop](./01-runaway-loop) — agent calls itself forever
2. [Stuck Agent](./02-stuck-agent) — can't recognize it's done
3. [Confidence Collapse](./03-confidence-collapse) — second-guesses every step

### Tool & Integration
4. [Tool Hallucination](./04-tool-hallucination) — invents tools that don't exist
5. [Silent Tool Failure](./05-silent-tool-failure) — treats errors as success
6. [Wrong Tool Pick](./06-wrong-tool-pick) — search when it should calculate

### State & Memory
7. [Context Collapse](./07-context-collapse) — forgets the original goal
8. [State Drift](./08-state-drift) — state quietly corrupts between steps
9. [Amnesia Bug](./09-amnesia-bug) — re-does work it already finished

### Trust & Safety
10. [Prompt Injection via Tool Output](./10-prompt-injection) — web page hijacks the agent
11. [Confident Liar](./11-confident-liar) — fabricates results instead of failing
12. [No Human Brake](./12-no-human-brake) — irreversible action, no checkpoint

---

## Quick start

```bash
git clone https://github.com/MenokoOG/agent-autopsy.git
cd agent-autopsy
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your API key

# Watch failure #1 break
cd 01-runaway-loop
python broken.py

# See the fix
python fixed.py
```

---

## Who this is for

- Engineers who've built an agent that worked once and never again
- Veteran AI builders who want failure case studies, not framework tours
- Teams putting agents in front of real users and need to know what to harden

Not for total beginners. If you've never written an API call, start elsewhere first.

---

## Philosophy

This repo follows the LAHA principle — **Love All Humans Always**. Every failure mode here is also a human-impact failure: wasted money, broken trust, decisions taken without consent. Building agents that fail safely isn't an engineering nicety. It's an ethical baseline.

Humans keep final authority over major decisions. Agents earn trust by being auditable, not by being autonomous.

---

## License

MIT. Use it, fork it, teach from it. Attribution appreciated.

## The written lessons

Full written walkthroughs of every failure — the diagnosis, the diff, and the production war story behind it — are being published as *The Agent Autopsy* series on freeCodeCamp. Link lands here when the first article ships.

---

*Built by [classHuman AI](https://classhuman.org) — driven by LAHA: Love All Humans Always.*
