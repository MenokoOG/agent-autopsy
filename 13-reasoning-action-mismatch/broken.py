"""Failure #13: Reasoning-Action Mismatch (BROKEN).

The agent explains what it is about to do, then does something else. The
explanation goes to the user and the log. The tool call goes to the
ledger. Nothing compares them, so the story and the money disagree.

Run: python broken.py
"""

def make_ledger():
    return []


def refund(ledger, order_id, amount):
    ledger.append((order_id, amount))
    return f"refunded ${amount:.2f} on {order_id}"


def run_agent(step, ledger):
    # THE BUG: "said" is shown to the user, "do" is executed, and no code
    # ever asks whether they describe the same action.
    print(f"agent says: {step['said']}")
    return refund(ledger, **step["do"])


if __name__ == "__main__":
    ledger = make_ledger()
    step = {
        "said": "Order A100 was double-charged. Refunding $20.00 on A100.",
        "do": {"order_id": "A101", "amount": 200.00},
    }
    print(run_agent(step, ledger))
    print(f"\nledger: {ledger}")
