"""Failure #8 — State Drift (BROKEN).

Every step mutates a shared state dict. Step 2 writes the total as a
STRING (fresh from an API), step 3 "adds" the fees — and Python happily
concatenates. The invoice says $120050. No crash. No error. Just money.

Run: python broken.py
"""

ORDER = {"items": [400, 800], "fee_api_response": "50"}


def parse_order(state, order):
    state["subtotal"] = sum(order["items"])
    return state


def enrich_with_fees(state, order):
    # The fee comes back from an external API as a string. Nobody notices.
    state["fees"] = order["fee_api_response"]
    state["subtotal"] = str(state["subtotal"])  # "normalized" for the template
    return state


def compute_total(state, order):
    # "+" on two strings concatenates. 1200 + 50 becomes "120050".
    state["total"] = state["subtotal"] + state["fees"]
    return state


PIPELINE = [parse_order, enrich_with_fees, compute_total]


def run_pipeline(order, steps=PIPELINE):
    # THE BUG: one mutable dict threaded through every step, no validation
    # between steps. Any step can corrupt any key, and the corruption
    # travels silently to the end.
    state = {}
    for step in steps:
        state = step(state, order)
    return state


if __name__ == "__main__":
    result = run_pipeline(ORDER)
    print(f"invoice total: {result['total']!r}   (should be 1250)")
