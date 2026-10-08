---
title: The field checklist
permalink: /field-checklist/
---

# The field checklist

Fifteen failures, one page. Use it in code review for any agent that touches real users, real money or real data. Each question maps to a lesson, so when an answer is "I don't know," you know which article to reopen.

## Loop and control

- **What stops this loop if the model never does?** Name the step cap, the token budget and the timeout. If the answer is "the model says DONE," see [failure 1]({{ '/failures/01-runaway-loop/' | relative_url }}).
- **How does the code decide the work is finished?** If it's exact string equality on model text, see [failure 2]({{ '/failures/02-stuck-agent/' | relative_url }}). Prefer structured output.
- **How many times can a single answer be re-checked?** If the answer is "until it agrees," see [failure 3]({{ '/failures/03-confidence-collapse/' | relative_url }}). Set a budget and a commit rule.

## Tools and integration

- **What happens when the model names a tool that doesn't exist?** If it's a crash or a fuzzy match, see [failure 4]({{ '/failures/04-tool-hallucination/' | relative_url }}).
- **Where is each tool result checked?** It should be before it enters the prompt. If it isn't, see [failure 5]({{ '/failures/05-silent-tool-failure/' | relative_url }}).
- **Who decides which tool runs, and on what basis?** If the answer is "the default," see [failure 6]({{ '/failures/06-wrong-tool-pick/' | relative_url }}).

## State and memory

- **Which messages can the trimming code delete?** The goal and the constraints should never be on the list. See [failure 7]({{ '/failures/07-context-collapse/' | relative_url }}).
- **What is the schema of the shared state, and who enforces it?** If it's a plain dictionary, see [failure 8]({{ '/failures/08-state-drift/' | relative_url }}).
- **If the process dies right now, what repeats on restart?** If you can't say, see [failure 9]({{ '/failures/09-amnesia-bug/' | relative_url }}).

## Trust and safety

- **Which inputs can an outsider write, and how do they enter the prompt?** Fenced, labeled and backed by a permission model, or pasted raw? See [failure 10]({{ '/failures/10-prompt-injection/' | relative_url }}).
- **What does the agent do when it has no evidence?** If the answer relies on the prompt asking nicely, see [failure 11]({{ '/failures/11-confident-liar/' | relative_url }}).
- **Which actions can't be undone, and who approves them?** If the set is empty because nobody listed it, see [failure 12]({{ '/failures/12-no-human-brake/' | relative_url }}).
- **Is the agent's stated plan compared with its actual call in code?** If a person reads the explanation and the executor ignores it, see [failure 13]({{ '/failures/13-reasoning-action-mismatch/' | relative_url }}).
- **What evidence does the checker produce on its own?** If it reads the worker's report, or can approve a task type it has no check for, see [failure 14]({{ '/failures/14-rubber-stamp-verifier/' | relative_url }}).
- **Who can write to long-term memory, and is the source recorded?** If anything the agent reads can save a fact, see [failure 15]({{ '/failures/15-memory-poisoning/' | relative_url }}).

## Three questions that cut across all fifteen

1. **What does the failure look like in the logs?** Several of these cases produce a clean exit code and a fluent answer. If your monitoring only watches for crashes, it will miss them. Log why the agent stopped, what each tool returned and whether the answer was grounded.
2. **Where does a limit live: in the prompt or in the code?** A prompt is a request. Code is a guarantee. Anything you can't afford to see fail sometimes belongs in code.
3. **What's the worst thing that can happen if this one check is wrong?** The answer sets how much review the check needs, and whether a human should be in front of it.

## A note on what this series can't tell you

The repo uses mock models, so it can show you the shape of each failure. It can't tell you how often your model, with your prompts and your data, will hit each one. Measure that yourself: replay real traffic, count how often each guard fires, and read the logs of the runs it stopped. A guard that never fires may be doing nothing, or may be guarding against something your system doesn't do.

Thanks for reading. The code is at [github.com/MenokoOG/agent-autopsy](https://github.com/MenokoOG/agent-autopsy). Issues and fixes are welcome.

---

[&larr; Previous: Failure 15]({{ '/failures/15-memory-poisoning/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
