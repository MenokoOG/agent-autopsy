---
title: "Failure 2: The stuck agent"
permalink: /failures/02-stuck-agent/
---

# Failure 2: The stuck agent

*The work was done on step one. The agent spent nineteen more steps failing to notice.*

## The scenario

Your agent has a step cap, so you already learned [the first lesson]({{ '/failures/01-runaway-loop/' | relative_url }}). It answers the question correctly and says it's finished. But your done-check looks for the exact string `TASK_COMPLETE`, and the model wrote "The task is complete." The agent decides it isn't done, asks the model to keep going, and does that until the cap runs out. Then it returns nothing. The right answer sat in the log the whole time.

The code is in [`02-stuck-agent`](https://github.com/MenokoOG/agent-autopsy/tree/main/agent-autopsy/02-stuck-agent).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/02-stuck-agent/broken.py):

```python
TASK = "What is the capital of France? Reply TASK_COMPLETE when done."
MAX_STEPS = 20  # a cap exists (lesson #1 learned) — but the done-check is broken

...

        if reply.strip() == "TASK_COMPLETE":
            return {"answer": reply, "steps": step}

        messages.append({"role": "user", "content": "Not done yet? Keep going."})

    return {"answer": None, "steps": max_steps}  # gave up holding the answer
```

The prompt asks for the reply `TASK_COMPLETE`. The mock model, like a real one, writes a sentence:

```text
step=1  The task is complete. The capital of France is Paris.
step=2  The task is complete. The capital of France is Paris.
step=3  The task is complete. The capital of France is Paris.
...
```

Twenty identical replies, each one an honest "I'm finished", each one rejected. Then `return {"answer": None, ...}`.

Two mistakes compound here.

First, the check uses equality on free-form text. `reply.strip() == "TASK_COMPLETE"` demands the model reproduce a token exactly, with no extra words. Models add words. They add a polite sentence, a period, a different capitalization, or the answer itself. Even the instruction in the prompt, "Reply TASK_COMPLETE when done", conflicts with the question being asked. The reply that carries the answer can't also be only a marker.

Second, the failure path throws away the answer. After 20 steps the function returns `None`, even though every reply in `messages` contained the answer. A "gave up" outcome should salvage what it has.

## Why it happens

Developers write the completion check once, test it against their own prompt, and move on. During testing the model might even comply with the exact format. Then the model version changes, or the prompt changes, or the question gets longer, and the format drifts. The check is a parser, but nobody wrote it like one.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/02-stuck-agent/fixed.py) makes two changes.

**Part 1: parse the signal tolerantly.**

```python
def is_complete(reply):
    return bool(re.search(r"(task|status)[\W_]*(is[\W_]*)?complete", reply, re.IGNORECASE))
```

That one regex matches `TASK_COMPLETE`, `Status: complete`, `STATUS: COMPLETE` and `The task is complete.` It ignores case and tolerates punctuation and underscores between the words. The prompt changes too: it now asks the model to end its reply with `STATUS: COMPLETE`, a marker that sits beside the answer instead of replacing it.

**Part 2: add a stall detector.**

```python
if reply == previous_reply:
    return {"answer": reply, "steps": step, "stopped_by": "stall"}
previous_reply = reply
```

If the model says exactly the same thing twice in a row, it isn't making progress. Asking a third time won't change that. The agent takes the reply it has and stops. Notice the return value: it gives back `reply` as the answer, where the broken version gave back `None`.

The loop now has four exits, each labeled: `signal`, `stall`, `max_steps`, and a fallback that returns `previous_reply`, the last thing the model said, instead of nothing.

Run it and the happy path finishes on the first step:

```text
stopped_by=signal steps=1
answer='The task is complete. The capital of France is Paris.'
```

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/02-stuck-agent/tests/test_fixed.py):

- `test_fixed_recognizes_natural_language_completion` checks the exact failure from the scenario now ends on the first step.
- `test_fixed_stall_detector_catches_repeats` uses a model that never signals completion but repeats itself, and checks the stall detector ends the run.
- `test_fixed_accepts_marker_variants` runs several phrasings through `is_complete`.
- `test_broken_burns_all_steps_holding_the_answer` keeps the bug on record: the broken version uses its whole step budget while the answer sits in its replies.

## Where the fix stops

A regex is still a guess about language, and it can go wrong in both directions.

- **False positives.** The pattern looks for "task" or "status" followed by "complete". A reply like "Status: complete data not found" would match. In a real system, prefer structured output. Ask the model to return JSON with a `status` field, or use the API's tool-call mechanism to signal completion, so you aren't parsing prose at all.
- **Stall detection needs exact repeats.** Two replies that differ by one word slip past `reply == previous_reply`. A model that rephrases the same answer each turn still loops until the cap. Production systems compare normalized text or embeddings, or track whether state changed between steps.
- **The stall exit can accept a bad answer.** If the model repeats a wrong answer, the stall detector returns it. Stalling tells you the agent is stuck. It says nothing about whether the answer is right. Pair it with the checks from later in this series.

## The takeaway

Completion detection is parsing, not string equality. Parse the signal tolerantly, prefer structured output where you can, and treat an agent that repeats itself as finished, with the answer in hand.

---

[&larr; Previous: Failure 1]({{ '/failures/01-runaway-loop/' | relative_url }}) · [Next: Failure 3, confidence collapse &rarr;]({{ '/failures/03-confidence-collapse/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
