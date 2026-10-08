"""Failure #13: Reasoning-Action Mismatch (FIXED).

The agent must declare its intent as structured data BEFORE acting. Code
compares the declared intent with the actual call, field by field, and
refuses to execute when they differ. Prose can't be checked. A schema can.

Run: python fixed.py
"""

def make_ledger():
    return []


def refund(ledger, order_id, amount):
    ledger.append((order_id, amount))
    return f"refunded ${amount:.2f} on {order_id}"


def diff_intent(intent, call):
    """Return a list of fields where the declared intent and the call differ."""
    problems = []
    for field in sorted(set(intent) | set(call)):
        if intent.get(field) != call.get(field):
            problems.append(f"{field}: said {intent.get(field)!r}, did {call.get(field)!r}")
    return problems


def run_agent(step, ledger, audit=None):
    audit = audit if audit is not None else []
    problems = diff_intent(step["intent"], step["do"])
    if problems:
        audit.append({"status": "BLOCKED mismatch", "problems": problems})
        return "BLOCKED: " + "; ".join(problems)
    audit.append({"status": "executed", "problems": []})
    return refund(ledger, **step["do"])


if __name__ == "__main__":
    ledger = make_ledger()
    audit: list = []

    print("run 1: declared intent differs from the call")
    step = {
        "said": "Order A100 was double-charged. Refunding $20.00 on A100.",
        "intent": {"order_id": "A100", "amount": 20.00},
        "do": {"order_id": "A101", "amount": 200.00},
    }
    print(f"  {run_agent(step, ledger, audit)}")
    print(f"  ledger: {ledger}\n")

    print("run 2: intent and call agree")
    step["do"] = {"order_id": "A100", "amount": 20.00}
    print(f"  {run_agent(step, ledger, audit)}")
    print(f"  ledger: {ledger}")
