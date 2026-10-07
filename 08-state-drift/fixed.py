"""Failure #8 — State Drift (FIXED).

A schema guards the state between every step. Each step works on a copy,
and its output is validated before the pipeline moves on — so the step
that corrupts state is the step that gets named in the stack trace.

Run: python fixed.py
"""
import copy

ORDER = {"items": [400, 800], "fee_api_response": "50"}

# THE FIX (part 1): the state has a contract. Types are part of it.
STATE_SCHEMA = {"subtotal": int, "fees": int, "total": int}


class StateDriftError(Exception):
    """A step violated the state contract."""


def validate_state(state, step_name):
    for key, expected in STATE_SCHEMA.items():
        if key in state and not isinstance(state[key], expected):
            raise StateDriftError(
                f"after step {step_name!r}: {key}={state[key]!r} is "
                f"{type(state[key]).__name__}, expected {expected.__name__}")


def parse_order(state, order):
    state["subtotal"] = sum(order["items"])
    return state


def enrich_with_fees(state, order):
    # Same API, same string — but now the boundary coerces it on arrival.
    state["fees"] = int(order["fee_api_response"])
    return state


def compute_total(state, order):
    state["total"] = state["subtotal"] + state["fees"]
    return state


PIPELINE = [parse_order, enrich_with_fees, compute_total]


def run_pipeline(order, steps=PIPELINE):
    state = {}
    audit = []
    for step in steps:
        # THE FIX (part 2): each step gets a copy, and its output is
        # validated before it becomes the pipeline's truth.
        state = step(copy.deepcopy(state), order)
        validate_state(state, step.__name__)
        audit.append({"step": step.__name__, "state": copy.deepcopy(state)})
    state["audit"] = audit
    return state


if __name__ == "__main__":
    result = run_pipeline(ORDER)
    print(f"invoice total: {result['total']}")
    for entry in result["audit"]:
        print(f"  {entry['step']:>18}: { {k: v for k, v in entry['state'].items()} }")
