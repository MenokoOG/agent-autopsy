"""Failure #9 — The Amnesia Bug (BROKEN).

The agent processes a work queue, crashes at item 3, and gets restarted
by the scheduler. It remembers nothing. Items 1 and 2 get processed again
— and "processed" means real emails to real customers, twice.

Run: python broken.py
"""

USERS = ["ana@example.com", "bo@example.com", "cy@example.com",
         "di@example.com", "ed@example.com"]


class TransientCrash(Exception):
    """The 2 a.m. network blip that kills the process mid-queue."""


def send_welcome_email(user, outbox):
    outbox.append(user)  # stands in for the real, irreversible side effect
    print(f"  sent welcome email to {user}")


def run_batch(users, outbox, crash_at=None):
    # THE BUG: no record of what's already done. Every run starts from
    # zero, and every completed side effect before a crash happens AGAIN
    # on the retry.
    for index, user in enumerate(users):
        if crash_at is not None and index == crash_at:
            raise TransientCrash(f"network blip at item {index}")
        send_welcome_email(user, outbox)


if __name__ == "__main__":
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
    print(f"\nusers emailed twice: {dupes}")
