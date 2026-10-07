---
title: "Failure 7: Context collapse"
permalink: /failures/07-context-collapse/
---

# Failure 7: Context collapse

*Thirty steps in, the agent forgot what it was hired to do, because the trimming code threw the goal away.*

## The scenario

A long-running agent fills its context window. To make room, your code keeps "the most recent N messages." Message 0 is the mission: migrate the billing database from MySQL to Postgres, and do not touch the auth service. It's also the oldest message, so it's the first one cut.

The agent keeps working, diligently, on whatever the recent messages talk about. Those messages mention the auth service's noisy logs. A billing migration turns into an auth refactor, and the one instruction that forbade it is gone.

The code is in [`07-context-collapse`](https://github.com/MenokoOG/agent-autopsy/tree/main/agent-autopsy/07-context-collapse).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/07-context-collapse/broken.py):

```python
GOAL = ("GOAL: Migrate the billing database from MySQL to Postgres. "
        "Do NOT touch the auth service.")
KEEP_LAST = 6  # naive context cap

def build_context(history, keep_last=KEEP_LAST):
    # THE BUG: "keep the last N" treats the goal like any other message.
    # Message 0 — the mission — is the first thing trimmed.
    return history[-keep_last:]
```

Each loop iteration appends a progress note that includes the aside "auth service logs look noisy btw", then calls the model on `build_context(history)`. After a few iterations, the window slides past the goal. The mock model behaves the way a real one has to: it can only act on what's in front of it.

```text
final reply: Recent messages mention the auth service — refactoring auth next!
goal still in context: False
```

The scenario uses ten steps and a window of six, so the effect shows up fast. In a real agent the same thing happens at step 40 with a window of 100 messages, and nobody sees it coming.

## Why it happens

"Keep the last N" is the simplest trimming rule, and it's recency-biased by design. For a chat that's usually right. For an agent, message 0 plays a different role than message 5. It's the specification. Everything after it is activity.

The model has no memory outside the prompt. If the goal isn't in the context, then as far as the model can tell, the goal doesn't exist. It won't flag the gap. It will steer by whatever it can read.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/07-context-collapse/fixed.py) pins the goal and trims the middle:

```python
def build_context(history, keep_last=KEEP_LAST):
    if len(history) <= keep_last + 1:
        return list(history)
    goal = history[0]
    dropped = len(history) - 1 - keep_last
    summary = {"role": "user",
               "content": f"[context note: {dropped} earlier progress messages "
                          "summarized away — no decisions were made in them]"}
    return [goal, summary] + history[-keep_last:]
```

The shape of the context is now: **goal, one marker line, recent tail.** The size is bounded, since it's always the goal plus a marker plus `keep_last` messages, which is 8 here. The goal is always present. The tail keeps the freshest detail.

Run it:

```text
final reply: Continuing the billing DB migration, step complete.
goal still in context: True
```

Look at the marker line, because it contains a claim: "no decisions were made in them". In this demo that's true, because the progress notes are noise. In a real agent it might not be. If you trim a message in which the user said "actually, skip the invoices table", your marker just erased a decision and told the model nothing important happened. This is the first place to be careful when you adapt the pattern.

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/07-context-collapse/tests/test_fixed.py):

- `test_fixed_pins_goal_after_heavy_trimming` checks the goal survives a long history.
- `test_fixed_context_stays_bounded` checks the window doesn't grow with the history.
- `test_fixed_keeps_most_recent_messages` checks the tail is intact.
- `test_fixed_agent_stays_on_mission` runs the full agent and checks its reply stays on the migration.
- `test_broken_loses_the_goal` pins the original failure.

## Where the fix stops

- **The summary line is a placeholder.** The demo replaces the middle with a fixed marker. A real system should summarize the middle, with a model or by extracting decisions, so that facts that matter survive. And it should keep decisions, constraints and open questions as first-class items instead of burying them in prose.
- **One pinned message may not be enough.** Real tasks have more than a goal: constraints, user preferences, a plan. Pin all of them, or store them as structured state outside the message list and re-inject them every turn.
- **Pinning doesn't make the model obey.** Having the goal in context raises the odds the agent follows it. A hard constraint like "do not touch the auth service" still needs enforcement in code, such as a tool-level permission that blocks writes to that service.
- **Token counts, not message counts.** `keep_last=6` counts messages. A single tool output can be thousands of tokens. Trim on tokens.

## The takeaway

Pin the goal, and trim the middle, never the ends. The agent can lose detail. It can't be allowed to lose the mission.

---

[&larr; Previous: Failure 6]({{ '/failures/06-wrong-tool-pick/' | relative_url }}) · [Next: Failure 8, state drift &rarr;]({{ '/failures/08-state-drift/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
