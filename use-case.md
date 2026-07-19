# Agent Autopsy — Use Case

**One-liner:** An open-source companion repo to my freeCodeCamp written lesson series — 12 real production failure modes of AI agents, each one runnable as `broken.py` and diagnosed in `fixed.py`.
**Status:** Shipped (MIT-licensed public repo; companion to *The Agent Autopsy* written series for freeCodeCamp), versioned with CHANGELOG
**Stack:** Python 3 (venv + requirements.txt), LLM API integration via .env keys, 12 self-contained failure-mode modules plus shared utilities

## Problem
Nearly every agent course teaches you to build one; almost none teach you what breaks when you ship one. Engineers hit runaway loops that burn tokens overnight, tools that fail silently, and agents that fabricate results instead of failing loud — and they debug each from scratch. This repo is the failure catalog I wished existed: production disasters made reproducible.

## What I Built
I catalogued 12 agent failure modes across four categories — loop & control (runaway loop, stuck agent, confidence collapse), tool & integration (tool hallucination, silent tool failure, wrong tool pick), state & memory (context collapse, state drift, amnesia bug), and trust & safety (prompt injection via tool output, confident liar, no human brake). Every failure is a pair of runnable scripts: `broken.py` reproduces the bug the way it happens in real systems, and `fixed.py` carries the lesson in the diff. The repo doubles as course infrastructure for *The Agent Autopsy: 12 Production Disasters, Diagnosed*, a written lesson series for freeCodeCamp, with its own versioning and documentation standards. The design philosophy is explicit: humans keep final authority, and agents earn trust by being auditable.

## Skills Demonstrated
Agent reliability engineering, failure-mode taxonomy design, production debugging patterns, prompt-injection defense, human-in-the-loop safeguards, Python, technical teaching and curriculum design, open-source repo hygiene (LICENSE, VERSIONING, CHANGELOG, DOCUMENTATION standards)

## Outcome / Evidence
Shipped: this is a public, MIT-licensed teaching repo tied to *The Agent Autopsy* freeCodeCamp series, built under my company (classHuman AI). Each of the 12 failure directories exists with runnable code, and the repo maintains formal versioning and changelog discipline. It is the most directly market-facing artifact in my portfolio.

## Interview Talking Points
- I can name and reproduce the 12 ways agents actually die in production — that taxonomy came from building and breaking real systems, not from framework docs.
- The broken.py/fixed.py pairing means every claim is executable: a hiring manager can run the failure and read the fix in the diff in under five minutes.
- It demonstrates I can package engineering experience into a sellable product — course, brand, license, versioning — end to end.

---
LAHA — Love All Humans Always.
