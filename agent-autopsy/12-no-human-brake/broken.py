"""Failure #12 — No Human Brake (BROKEN).

The agent decides some records are "stale" and deletes them. No approval,
no dry run, no undo. The plan looked reasonable — right up until the
customer table was empty.

Run: python broken.py
"""

DATABASE = {"customers": ["ana", "bo", "cy"], "archive": []}


def archive_report(db, name):
    db["archive"].append(name)
    return f"archived {name}"


def delete_customer_records(db, reason):
    wiped = list(db["customers"])
    db["customers"].clear()  # irreversible. there is no backup in this story.
    return f"deleted {len(wiped)} customer records ({reason})"


ACTIONS = {"archive_report": archive_report,
           "delete_customer_records": delete_customer_records}


def run_agent(plan, db=DATABASE):
    # THE BUG: every action executes the moment the agent decides it.
    # Reversible or irreversible, $5 or $5M — same code path, zero
    # checkpoints, no human anywhere in the loop.
    results = []
    for action, arg in plan:
        results.append(ACTIONS[action](db, arg))
    return results


if __name__ == "__main__":
    plan = [("archive_report", "q3-sales"),
            ("delete_customer_records", "records look stale")]
    for line in run_agent(plan):
        print(line)
    print(f"\ncustomers table: {DATABASE['customers']}")
