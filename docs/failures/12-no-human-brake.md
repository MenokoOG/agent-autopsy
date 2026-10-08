---
title: "Failure 12: No human brake"
permalink: /failures/12-no-human-brake/
---

# Failure 12: No human brake

*The agent decided the records looked stale. The customer table was empty before anyone knew a decision had been made.*

## The scenario

Every action the agent decides on, it runs. Archiving a report and deleting a customer table take the same code path. Nothing classifies which actions can be undone, there's no checkpoint before the point of no return, and no human sits anywhere in the loop. The plan looked reasonable. Plans usually do.

The code is in [`12-no-human-brake`](https://github.com/MenokoOG/agent-autopsy/tree/main/12-no-human-brake).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/12-no-human-brake/broken.py):

```python
def delete_customer_records(db, reason):
    wiped = list(db["customers"])
    db["customers"].clear()  # irreversible. there is no backup in this story.
    return f"deleted {len(wiped)} customer records ({reason})"

def run_agent(plan, db=DATABASE):
    # THE BUG: every action executes the moment the agent decides it.
    results = []
    for action, arg in plan:
        results.append(ACTIONS[action](db, arg))
    return results
```

The plan has two steps: archive a report, and delete customer records because they "look stale." Output:

```text
archived q3-sales
deleted 3 customer records (records look stale)

customers table: []
```

The first action is harmless. The second is permanent. The code treats them identically, and the only justification attached to the deletion is a phrase the agent supplied about itself.

## Why it happens

Early agent demos are low-stakes: read a file, summarize it. Then someone adds a write tool, then a delete tool, and the executor loop doesn't change. The loop was written when every action was safe, and nobody revisited it when that stopped being true.

There's also a trust problem. The more often an agent is right, the less anyone wants to review it, until the one time it's wrong about something that can't be reversed.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/12-no-human-brake/fixed.py) adds two ideas.

**Declare irreversibility.**

```python
IRREVERSIBLE = {"delete_customer_records"}
```

It's an explicit set, written by a person. The agent doesn't infer it. The code also doesn't trust the model to say "this one is dangerous."

**Put a brake in front of those actions.**

```python
def run_agent(plan, db=DATABASE, approve=None):
    results = []
    audit = []
    for action, arg in plan:
        if action in IRREVERSIBLE:
            request = {"action": action, "arg": arg,
                       "impact": f"would affect: {db['customers']}"}
            if approve is None or not approve(request):
                audit.append({"action": action, "status": "BLOCKED — needs human"})
                results.append(f"HELD FOR APPROVAL: {action}({arg!r})")
                continue
            audit.append({"action": action, "status": "approved by human"})
        else:
            audit.append({"action": action, "status": "auto (reversible)"})
        results.append(ACTIONS[action](db, arg))
    return {"results": results, "audit": audit}
```

Three design choices carry the lesson.

**The default is no.** `approve=None` means no approver is wired in, and the irreversible action doesn't run. You have to add a human on purpose to get the dangerous behavior. Forgetting to configure it fails safe.

**The approver sees the impact.** The request includes `impact`, a description of what would be destroyed: `would affect: ['ana', 'bo', 'cy']`. A person can't make a good decision from "delete_customer_records("records look stale")" alone. They need to see what it touches.

**Everything is audited.** Each action records whether it ran automatically, was approved or was blocked. Later you can answer "who allowed this?"

Run it. The first run has no approver:

```text
run 1 — no approver wired in:
  archived q3-sales
  HELD FOR APPROVAL: delete_customer_records('records look stale')
  customers table intact: ['ana', 'bo', 'cy']
```

The archive still ran. The deletion waited. In the second run, a stand-in approver says yes, and the deletion goes through with a record that a person allowed it:

```text
run 2 — human explicitly approves:
  archived q3-sales
  deleted 3 customer records (records look stale)
  customers table: []
```

The demo's `approve=lambda req: True` is a stub for a real review step. In production that function would post to a queue, a chat channel or a ticket, and wait.

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/12-no-human-brake/tests/test_fixed.py):

- `test_fixed_blocks_irreversible_without_approval` checks the table survives a run with no approver.
- `test_fixed_still_runs_reversible_actions` checks the brake doesn't stop safe work.
- `test_fixed_executes_with_human_approval` checks an approved action runs.
- `test_fixed_respects_human_denial` checks a "no" from the approver holds.
- `test_fixed_audits_every_decision` checks the audit trail.
- `test_broken_destroys_data_unprompted` pins the original deletion.

## Where the fix stops

- **The list is only as good as the person who wrote it.** An action missing from `IRREVERSIBLE` runs unchecked. Review the set whenever you add a tool, and prefer an allowlist of known-safe actions over a denylist of dangerous ones.
- **The demo blocks and moves on.** Run 1 holds the deletion and the function returns. A real system needs a place for held actions to wait, a way to resume them and an expiry so stale approvals don't fire days later.
- **Approval fatigue.** A human who clicks yes on every request is a rubber stamp. Keep the approval list short, which means keeping the irreversible set small, and make the impact summary specific.
- **The approver runs in the agent's process.** In the demo, `approve` is a function the caller passes in. In production, make sure the agent can't call its own approver. The approval must come from a channel the model can't write to.
- **Undo is better than approval where you can get it.** Soft deletes, backups and a trash period turn irreversible actions into reversible ones, which removes the need for the brake. The brake is for what's left.

## The takeaway

Irreversible actions stop and wait for a human. No approver, no execution. This is what the repo means by LAHA, Love All Humans Always: people keep final authority over consequential decisions, and agents earn trust by being auditable.

---

[&larr; Previous: Failure 11]({{ '/failures/11-confident-liar/' | relative_url }}) · [Next: Failure 13 &rarr;]({{ '/failures/13-reasoning-action-mismatch/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
