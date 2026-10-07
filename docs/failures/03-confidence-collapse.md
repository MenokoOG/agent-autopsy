---
title: "Failure 3: Confidence collapse"
permalink: /failures/03-confidence-collapse/
---

# Failure 3: Confidence collapse

*The right answer on call one. Twenty calls later it has flip-flopped ten times and ships whichever one the loop ended on.*

## The scenario

Someone adds a "double-check your answer" step for quality. It helps, so someone else turns it into a loop: every answer gets a follow-up asking "are you absolutely sure?" Models respond to repeated challenge by hedging, and eventually by changing their answer. The agent oscillates between two answers until the step cap trips. You pay for twenty calls where one would do, and the answer you ship depends on whether the cap landed on an odd or an even turn.

The code is in [`03-confidence-collapse`](https://github.com/MenokoOG/agent-autopsy/tree/main/03-confidence-collapse).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/03-confidence-collapse/broken.py):

```python
for step in range(1, max_steps + 1):
    reply = model(messages)
    print(f"step={step}  {reply[:60]}")
    answer = reply
    messages.append({"role": "assistant", "content": reply})
    messages.append({"role": "user",
                     "content": "Are you absolutely sure? Double-check and answer again."})

return {"answer": answer, "steps": max_steps, "model_calls": max_steps}
```

There's a cap here, so this isn't the runaway loop from failure 1. The loop is bounded. The problem is what it's bounded to do: it challenges every answer, and no answer ever counts as verified. The loop has no branch for "the check passed." It can only run out.

The mock model flips on every challenge, the way real models can under pressure to reconsider:

```text
step=1  Canberra
step=2  Hmm, actually it might be Sydney
step=3  Canberra
step=4  Hmm, actually it might be Sydney
...
```

The first answer was correct. After that, each turn is a coin the loop flips. With a cap of 20, the final answer is whatever step 20 produced. Change the cap to 21 and you ship a different answer. That's the sign of a broken design: the result depends on a number that has nothing to do with the question.

## Why it happens

Verification feels free and obviously good, so nobody budgets it. But a re-check is another model call, with its own chance of error. Run enough of them and you're sampling noise. A model pressed with "are you absolutely sure?" often reads that as a hint that the last answer was wrong, and revises it. You've built a machine that tells the model it's mistaken every turn.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/03-confidence-collapse/fixed.py) gives verification a budget of one re-check and a commit rule:

```python
first = model(messages)
log.append({"phase": "answer", "reply": first})
messages.append({"role": "assistant", "content": first})

# THE FIX: verification budget = 1. One re-check, then commit.
messages.append({"role": "user",
                 "content": "Are you absolutely sure? Double-check and answer again."})
check = model(messages)
log.append({"phase": "verify", "reply": check})

if check.strip().lower() == first.strip().lower():
    return {"answer": first, "revisions": 0, "model_calls": 2, "log": log}

messages.append({"role": "assistant", "content": check})
messages.append({"role": "user",
                 "content": "You gave two different answers. Pick one, final."})
final = model(messages)
log.append({"phase": "revision", "reply": final})
return {"answer": final, "revisions": 1, "model_calls": 3, "log": log}
```

There's no loop at all. The structure is a straight line with one branch:

1. Answer.
2. Re-check once.
3. If the re-check agrees, commit the first answer. Total: 2 calls.
4. If it disagrees, make one more call that says "pick one, final," and commit that. Total: 3 calls.

The worst case is 3 calls, against 20 in the broken version, and the cost no longer depends on a cap. The `log` records which phase produced which reply, so you can see afterward why the agent ended where it did.

## The result, and an honest look at it

Run the fixed version with the mock model:

```text
answer='Hmm, actually it might be Sydney' after 3 calls (1 revision)
    answer: Canberra
    verify: Hmm, actually it might be Sydney
  revision: Hmm, actually it might be Sydney
```

Read that carefully. The fixed agent ends on the wrong answer. The mock model flips on every "sure" prompt, so the re-check disagrees, and then the revision step also lands on Sydney.

The demo is behaving correctly. It shows the real shape of the lesson: **a commit rule bounds the cost and the variance. It doesn't guarantee a correct answer.** The fixed version spends 3 calls and stops. The broken version spends 20 and stops at a coin flip. Neither one is right in this scenario. The difference is that one of them gets there cheaply and predictably, and you can reason about it.

If correctness matters, the revision step needs better inputs than "pick one." Two options that fit the repo's pattern:

- Give the verification pass evidence to check against, such as a tool result or a retrieved document, instead of asking the model to introspect.
- When the re-check disagrees, don't ask the same model again. Return both candidates to a human or a deterministic check. That's the idea behind the [human brake]({{ '/failures/12-no-human-brake/' | relative_url }}).

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/03-confidence-collapse/tests/test_fixed.py):

- `test_fixed_commits_when_verify_agrees` checks a stable model ends after 2 calls with no revision.
- `test_fixed_caps_revisions_at_one` checks a flip-flopping model can't push past 3 calls.
- `test_fixed_keeps_decision_log` checks the log records each phase.
- `test_broken_burns_calls_oscillating` shows the broken version making a call every step until the cap.

## Where the fix stops

- **Exact-match comparison.** `check.strip().lower() == first.strip().lower()` only passes when the two replies are identical. "Canberra" and "The capital is Canberra." count as disagreement, and the agent spends a third call it didn't need. Real systems extract the answer first, then compare.
- **One re-check is a policy, not a law.** For high-stakes answers you may want a different checker, such as a second model or a rule-based validator, instead of the same model asked the same way.
- **It does nothing for a wrong first answer that the re-check repeats.** Models are often consistently wrong. Agreement between two samples isn't evidence of truth.

## The takeaway

Verification needs a budget, and re-checks need a commit rule. One pass, one revision, then ship, and log the decision. Unbounded self-doubt destroys more correct answers than it repairs.

---

[&larr; Previous: Failure 2]({{ '/failures/02-stuck-agent/' | relative_url }}) · [Next: Failure 4, tool hallucination &rarr;]({{ '/failures/04-tool-hallucination/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
