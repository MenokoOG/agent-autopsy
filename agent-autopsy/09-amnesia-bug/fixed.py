"""Failure #9 — The Amnesia Bug (FIXED).

A durable checkpoint file records every completed item BEFORE the next one
starts. On restart, the agent reads the checkpoint and skips finished work.
Crash all you want — each side effect happens exactly once.

Run: python fixed.py
"""
import json
from pathlib import Path

USERS = ["ana@example.com", "bo@example.com", "cy@example.com",
         "di@example.com", "ed@example.com"]
CHECKPOINT = Path("checkpoint.jsonl")


class TransientCrash(Exception):
    """The 2 a.m. network blip that kills the process mid-queue."""


def send_welcome_email(user, outbox):
    outbox.append(user)
    print(f"  sent welcome email to {user}")


def load_done(checkpoint):
    if not checkpoint.exists():
        return set()
    return {json.loads(line)["id"] for line in checkpoint.read_text().splitlines()}


def mark_done(checkpoint, item_id):
    # Append-and-flush BEFORE moving on. If we crash after this line,
    # the item is safe; if we crash before it, the item retries. Either
    # way: at-most-once past this point, at-least-once before it.
    with checkpoint.open("a") as f:
        f.write(json.dumps({"id": item_id}) + "\n")


def run_batch(users, outbox, checkpoint=CHECKPOINT, crash_at=None):
    # THE FIX: consult the work log first, record completion durably.
    done = load_done(checkpoint)
    for index, user in enumerate(users):
        if user in done:
            continue  # already completed on a previous run — skip
        if crash_at is not None and index == crash_at:
            raise TransientCrash(f"network blip at item {index}")
        send_welcome_email(user, outbox)
        mark_done(checkpoint, user)


if __name__ == "__main__":
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()
    outbox = []
    print("first run (crashes at item 3):")
    try:
        run_batch(USERS, outbox, crash_at=3)
    except TransientCrash as crash:
        print(f"  CRASH: {crash}")

    print("scheduler retries:")
    run_batch(USERS, outbox)

    from collections import Counter
    dupes = {u: n for u, n in Counter(outbox).items() if n > 1}
    print(f"\nusers emailed twice: {dupes or 'none'}")
    CHECKPOINT.unlink()
