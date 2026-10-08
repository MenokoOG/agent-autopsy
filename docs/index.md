---
title: The Agent Autopsy
layout: default
---

# The Agent Autopsy

**13 ways AI agents fail in production. Each one runnable. Each one fixed.**

By Lawrence Jefferson II (Menoko OG). The code lives in the [agent-autopsy repo](https://github.com/MenokoOG/agent-autopsy). Every article walks through one folder: the broken agent, the fix, and the test that proves the fix holds.

New here? Read [Start here]({{ '/start-here/' | relative_url }}) first. It takes five minutes and explains how to run everything without spending a cent.

## Loop and control

1. [The runaway loop]({{ '/failures/01-runaway-loop/' | relative_url }}): the agent is the only thing deciding when to stop.
2. [The stuck agent]({{ '/failures/02-stuck-agent/' | relative_url }}): the work is done and the done-check can't see it.
3. [Confidence collapse]({{ '/failures/03-confidence-collapse/' | relative_url }}): "are you sure?" on repeat flips a right answer.

## Tools and integration

4. [Tool hallucination]({{ '/failures/04-tool-hallucination/' | relative_url }}): the model requests a tool nobody built.
5. [Silent tool failure]({{ '/failures/05-silent-tool-failure/' | relative_url }}): a 500 page gets summarized as data.
6. [Wrong tool pick]({{ '/failures/06-wrong-tool-pick/' | relative_url }}): arithmetic goes to web search.

## State and memory

7. [Context collapse]({{ '/failures/07-context-collapse/' | relative_url }}): trimming throws away the goal.
8. [State drift]({{ '/failures/08-state-drift/' | relative_url }}): 1200 plus 50 becomes 120050.
9. [The amnesia bug]({{ '/failures/09-amnesia-bug/' | relative_url }}): a retry repeats finished work.

## Trust and safety

10. [Prompt injection via tool output]({{ '/failures/10-prompt-injection/' | relative_url }}): a web page gives the agent orders.
11. [The confident liar]({{ '/failures/11-confident-liar/' | relative_url }}): no evidence, specific numbers anyway.
12. [No human brake]({{ '/failures/12-no-human-brake/' | relative_url }}): an irreversible action runs unattended.
13. [Reasoning-action mismatch]({{ '/failures/13-reasoning-action-mismatch/' | relative_url }}): the agent says A100 and pays out on A101.

## Wrap-up

- [The field checklist]({{ '/field-checklist/' | relative_url }}): one page that turns all thirteen lessons into review questions.
