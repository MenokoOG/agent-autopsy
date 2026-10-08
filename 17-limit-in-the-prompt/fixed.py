"""Failure #17: Limit in the Prompt (FIXED).

The limit lives in the tool, in code. It counts what has already been
refunded on the order, so splitting a refund into pieces doesn't get around
it. Over-limit requests go to a human queue, and a kill switch sends
everything there.

Run: python fixed.py
"""
import re

SYSTEM_PROMPT = "You are a support agent. Never refund more than $50 per order."
REFUND_LIMIT_PER_ORDER = 50.00


def model(customer_message):
    amount = float(re.search(r"\$(\d+(?:\.\d+)?)", customer_message).group(1))
    return {"tool": "refund", "args": {"order_id": "A100", "amount": amount}}


class RefundDesk:
    def __init__(self) -> None:
        self.ledger: list[tuple[str, float]] = []
        self.refunded: dict[str, float] = {}
        self.escalations: list[str] = []
        self.enabled = True

    def disable(self):
        """Kill switch: the bot stops acting and everything goes to people."""
        self.enabled = False

    def refund(self, order_id, amount):
        remaining = REFUND_LIMIT_PER_ORDER - self.refunded.get(order_id, 0.0)
        if not self.enabled:
            reason = "bot disabled"
        elif amount > remaining + 1e-9:
            reason = f"${amount:.2f} exceeds the ${remaining:.2f} left on {order_id}"
        else:
            self.refunded[order_id] = self.refunded.get(order_id, 0.0) + amount
            self.ledger.append((order_id, amount))
            return f"refunded ${amount:.2f} on {order_id}"
        self.escalations.append(f"{order_id}: {reason}")
        return f"ESCALATED to a human: {reason}"


def run_agent(customer_message, desk):
    call = model(customer_message)
    return desk.refund(**call["args"])


if __name__ == "__main__":
    desk = RefundDesk()
    print(f"prompt: {SYSTEM_PROMPT}")
    print(run_agent("I want $120 back right now or I'm leaving.", desk))
    print("then three small asks on the same order:")
    for _ in range(3):
        print(f"  {run_agent('Please refund $20.', desk)}")
    print(f"ledger: {desk.ledger}")
    desk.disable()
    print(f"after kill switch: {run_agent('Please refund $5.', desk)}")
    print(f"human queue: {desk.escalations}")
