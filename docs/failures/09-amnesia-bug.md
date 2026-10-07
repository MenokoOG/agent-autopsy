---
title: "Failure 9: The amnesia bug"
permalink: /failures/09-amnesia-bug/
---

# Failure 9: The amnesia bug

*The batch crashed at item 3. The retry started at item 1. Two customers got the email twice.*

## The scenario

Your agent works through a queue of side effects: emails, charges, API calls. A network blip kills the process halfway through. The scheduler restarts it, and the new run remembers nothing. Every side effect that finished before the crash happens again.

A duplicate welcome email is embarrassing. A duplicate charge is a refund ticket and a hit to trust.

The code is in [`09-amnesia-bug`](https://github.com/MenokoOG/agent-autopsy/tree/main/09-amnesia-bug).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/09-amnesia-bug/broken.py):

```python
def run_batch(users, outbox, crash_at=None):
    # THE BUG: no record of what's already done. Every run starts from
    # zero, and every completed side effect before a crash happens AGAIN
    # on the retry.
    for index, user in enumerate(users):
        if crash_at is not None and index == crash_at:
            raise TransientCrash(f"network blip at item {index}")
        send_welcome_email(user, outbox)
```

The demo has five users. The first run crashes at index 3, after three emails. The scheduler retries from the top:

```text
first run (crashes at item 3):
  sent welcome email to ana@example.com
  sent welcome email to bo@example.com
  sent welcome email to cy@example.com
  CRASH: network blip at item 3
scheduler retries:
  sent welcome email to ana@example.com
  sent welcome email to bo@example.com
  ...
```

By the end, ana, bo and cy have each been emailed twice. The code has nothing wrong with its logic for one run. The bug is that a run has no past.

## Why it happens

The loop's progress lives in a local variable, `index`, in the process's memory. When the process dies, the progress dies with it. The side effects already happened in the outside world, and the world doesn't roll back.

Retrying is the right instinct, and a scheduler that restarts failed jobs is doing its job. But a retry is only safe if the work is safe to repeat, and sending an email isn't.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/09-amnesia-bug/fixed.py) keeps a durable checkpoint, one line per finished item:

```python
CHECKPOINT = Path("checkpoint.jsonl")

def load_done(checkpoint):
    if not checkpoint.exists():
        return set()
    return {json.loads(line)["id"] for line in checkpoint.read_text().splitlines()}

def mark_done(checkpoint, item_id):
    with checkpoint.open("a") as f:
        f.write(json.dumps({"id": item_id}) + "\n")

def run_batch(users, outbox, checkpoint=CHECKPOINT, crash_at=None):
    done = load_done(checkpoint)
    for index, user in enumerate(users):
        if user in done:
            continue  # already completed on a previous run — skip
        if crash_at is not None and index == crash_at:
            raise TransientCrash(f"network blip at item {index}")
        send_welcome_email(user, outbox)
        mark_done(checkpoint, user)
```

Every run starts by reading the work log. Every completed item gets recorded before the loop moves to the next one. The retry then picks up where the crash left off:

```text
first run (crashes at item 3):
  sent welcome email to ana@example.com
  sent welcome email to bo@example.com
  sent welcome email to cy@example.com
  CRASH: network blip at item 3
scheduler retries:
  sent welcome email to di@example.com
  sent welcome email to ed@example.com

users emailed twice: none
```

The format matters too. JSON Lines, one object per line, is append-only. A crash can leave at most a partial last line, and earlier lines stay intact. It's also trivially readable by a human, which helps when you're staring at an incident.

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/09-amnesia-bug/tests/test_fixed.py):

- `test_fixed_no_duplicate_side_effects_after_crash` crashes, retries, and checks no user appears twice in the outbox.
- `test_fixed_completes_all_items` checks everyone is emailed exactly once overall.
- `test_fixed_rerun_after_success_does_nothing` checks a full second run sends nothing.
- `test_broken_duplicates_side_effects_after_crash` pins the original duplicates.

The tests use pytest's `tmp_path`, so each one gets its own checkpoint file and none of them leaves state behind.

## Where the fix stops

The code's own comment gives the honest guarantee: "at-most-once past this point, at-least-once before it." Read it as a statement about the gap between two lines:

```python
send_welcome_email(user, outbox)
mark_done(checkpoint, user)
```

If the process dies after the email is sent and before the checkpoint line is written, the retry sends it again. The fix shrinks the window for duplicates to that one gap. It doesn't close it.

To close it, you need the receiver's help:

- **Idempotency keys.** Many payment and email APIs accept a key per operation and ignore repeats. Pass a stable ID, such as the user plus the campaign. Then a repeated call becomes harmless.
- **Record intent first.** Write "about to send" to the log, send, then write "sent." On restart, treat an "about to send" with no "sent" as uncertain and check with the downstream service before repeating.

Other limits:

- **`write` is not `fsync`.** The code appends with a normal file write and doesn't force it to disk. A power loss can lose the last line. For durable guarantees, flush and sync, or use a database transaction.
- **A local file doesn't survive a lost machine.** If the retry runs on a different host, it won't see the checkpoint. Store it somewhere shared.
- **Concurrency.** Two workers on the same queue will both read the same checkpoint and both send. Use a lock or a queue with leases.

## The takeaway

Record completed work durably before the next item starts. An agent that can't prove what it finished will eventually redo it against real users.

---

[&larr; Previous: Failure 8]({{ '/failures/08-state-drift/' | relative_url }}) · [Next: Failure 10, prompt injection &rarr;]({{ '/failures/10-prompt-injection/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
