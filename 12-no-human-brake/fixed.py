"""Failure #12 — No Human Brake (FIXED).

Actions are classified: reversible ones run, irreversible ones STOP and
wait for a human. The agent prepares everything — what, why, what it will
destroy — and a person makes the call. LAHA: humans keep final authority.

Run: python fixed.py
"""

DATABASE = {"customers": ["ana", "bo", "cy"], "archive": []}


class ApprovalRequired(Exception):
    """An irreversible action reached the brake with no human approval."""


def archive_report(db, name):
    db["archive"].append(name)
    return f"archived {name}"


def delete_customer_records(db, reason):
    wiped = list(db["customers"])
    db["customers"].clear()
    return f"deleted {len(wiped)} customer records ({reason})"


ACTIONS = {"archive_report": archive_report,
           "delete_customer_records": delete_customer_records}

# THE FIX (part 1): irreversibility is declared, not inferred.
IRREVERSIBLE = {"delete_customer_records"}


def run_agent(plan, db=DATABASE, approve=None):
    # THE FIX (part 2): the brake. Irreversible actions require an explicit
    # human decision, made with full context. No approver = no execution.
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


if __name__ == "__main__":
    plan = [("archive_report", "q3-sales"),
            ("delete_customer_records", "records look stale")]

    print("run 1 — no approver wired in:")
    outcome = run_agent(plan)
    for line in outcome["results"]:
        print(f"  {line}")
    print(f"  customers table intact: {DATABASE['customers']}\n")

    print("run 2 — human explicitly approves:")
    outcome = run_agent(plan, approve=lambda req: True)
    for line in outcome["results"]:
        print(f"  {line}")
    print(f"  customers table: {DATABASE['customers']}")
