---
title: "Failure 13: Reasoning-action mismatch"
permalink: /failures/13-reasoning-action-mismatch/
---

# Failure 13: Reasoning-action mismatch

*The agent said it would refund $20.00 on order A100. The ledger shows $200.00 paid out on A101.*

## The scenario

An agent handles refund tickets. For each one it writes a short explanation of what it's about to do, then calls a tool. The explanation goes to the customer and to the log. The tool call goes to the payments system. Nothing in the code compares the two.

This is a documented failure mode in multi-agent systems. The MAST study annotated 1,642 execution traces from seven multi-agent frameworks and labeled it "reasoning-action mismatch": the agent's actions contradict its own stated reasoning. It accounts for 13.2% of the failures the authors recorded, the largest share in the inter-agent misalignment group ([Cemri et al., 2025](https://arxiv.org/abs/2503.13657)).

The code is in [`13-reasoning-action-mismatch`](https://github.com/MenokoOG/agent-autopsy/tree/main/13-reasoning-action-mismatch). Like the rest of this series, it's a demonstration in code. It isn't a measurement of how often a real model does this.

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/13-reasoning-action-mismatch/broken.py):

```python
def run_agent(step, ledger):
    # THE BUG: "said" is shown to the user, "do" is executed, and no code
    # ever asks whether they describe the same action.
    print(f"agent says: {step['said']}")
    return refund(ledger, **step["do"])
```

The step carries two things: what the agent said, and what it did. The run:

```text
agent says: Order A100 was double-charged. Refunding $20.00 on A100.
refunded $200.00 on A101

ledger: [('A101', 200.0)]
```

The explanation is reasonable, and the action contradicts it on two fields. A person reading the log sees a sensible plan. The money went somewhere else.

## Why it happens

The explanation and the tool call are two separate outputs of a language model. Nothing forces them to agree. The model can write a correct plan and then emit arguments from a different order it saw earlier in the context, a stale value or a neighboring record. Long contexts and several similar records make this easier to hit.

The code makes it worse. The explanation looks like a safety feature, because a human can read it. But a reader trusts it as a description of the action, and the executor ignores it. The only thing the system acts on is the call.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/13-reasoning-action-mismatch/fixed.py) changes what the agent has to hand over.

**Declare intent as data.**

```python
step = {
    "said": "Order A100 was double-charged. Refunding $20.00 on A100.",
    "intent": {"order_id": "A100", "amount": 20.00},
    "do": {"order_id": "A101", "amount": 200.00},
}
```

Prose can't be checked by code. A structured `intent` can. The agent still writes `said` for the human, but the executor only trusts `intent`.

**Diff the intent against the call.**

```python
def diff_intent(intent, call):
    problems = []
    for field in sorted(set(intent) | set(call)):
        if intent.get(field) != call.get(field):
            problems.append(f"{field}: said {intent.get(field)!r}, did {call.get(field)!r}")
    return problems
```

It checks every field in either dictionary, so an extra argument in the call counts as a mismatch too.

**Block on any difference.**

```python
def run_agent(step, ledger, audit=None):
    audit = audit if audit is not None else []
    problems = diff_intent(step["intent"], step["do"])
    if problems:
        audit.append({"status": "BLOCKED mismatch", "problems": problems})
        return "BLOCKED: " + "; ".join(problems)
    audit.append({"status": "executed", "problems": []})
    return refund(ledger, **step["do"])
```

The ledger is untouched when the check fails, and the audit record names the fields. Run it:

```text
run 1: declared intent differs from the call
  BLOCKED: amount: said 20.0, did 200.0; order_id: said 'A100', did 'A101'
  ledger: []

run 2: intent and call agree
  refunded $20.00 on A100
  ledger: [('A100', 20.0)]
```

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/13-reasoning-action-mismatch/tests/test_fixed.py):

- `test_fixed_blocks_when_call_differs_from_intent` checks the ledger stays empty.
- `test_fixed_runs_when_intent_matches_call` checks a consistent step still runs.
- `test_fixed_reports_every_differing_field` checks both mismatched fields are named.
- `test_fixed_blocks_an_extra_field_in_the_call` checks an argument the agent never declared counts as a difference.
- `test_fixed_audits_blocked_and_executed` checks the audit trail.
- `test_broken_refunds_the_wrong_order_while_saying_otherwise` pins the original failure.

## Where the fix stops

- **A model that is consistently wrong passes.** If the model declares A101 and calls A101, the diff finds nothing. This check catches disagreement between two outputs. It doesn't know which order the ticket was about. Check the call against the ticket, the order total and the customer, using data the model can't write.
- **Both outputs come from the same model.** A prompt injection that changes the plan changes the intent and the call together. See [failure 10]({{ '/failures/10-prompt-injection/' | relative_url }}).
- **Free-text reasoning is out of reach.** The check works because `intent` is a schema. Chain-of-thought prose can't be diffed, so don't try to grade it with string matching.
- **Equality can be too strict.** `20` and `20.0` compare equal in Python, but `"20.00"` doesn't. Normalize types and formats before you compare, and decide what a near match means for amounts.
- **A block needs somewhere to go.** The demo returns a message. A real system should send the mismatch back to the model for one bounded retry, then escalate to a person. See [failure 12]({{ '/failures/12-no-human-brake/' | relative_url }}).

## The takeaway

An agent's explanation is a claim, so make it structured and check it against the call in code before anything runs.

---

[&larr; Previous: Failure 12]({{ '/failures/12-no-human-brake/' | relative_url }}) · [Next: The field checklist &rarr;]({{ '/field-checklist/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
