---
title: "Failure 8: State drift"
permalink: /failures/08-state-drift/
---

# Failure 8: State drift

*The invoice said 120050. The math was 1200 plus 50. Nothing crashed.*

## The scenario

A pipeline threads one shared state dictionary through several steps. One step stores a number as a string, because that's what an external API handed back. Two steps later, `+` meets two strings and concatenates them. There's no exception and no log line. A wrong number moves quietly toward a customer.

String-typed totals are one example. Swapped keys and stale fields behave the same way. State corrupts between steps, and by the time you see the damage you can't tell which step caused it.

The code is in [`08-state-drift`](https://github.com/MenokoOG/agent-autopsy/tree/main/08-state-drift).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/08-state-drift/broken.py):

```python
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
```

Three small decisions combine into the bug. The fee arrives as the string `"50"`. A helpful step converts the subtotal to a string "for the template". And the total step adds the two. In Python, `"1200" + "50"` is `"120050"`:

```text
invoice total: '120050'   (should be 1250)
```

Note that there are two separate mistakes. The fee should have been converted to a number when it arrived. And `enrich_with_fees` turned the subtotal into a string, which no later step expects. Either one alone might have been survivable. Together they produced a value that looks like a plausible amount.

## Why it happens

A single mutable dictionary passed through every step has no contract. Any step can write any key with any type, and every later step has to guess what it'll find. Dynamic typing makes this easy to write, and the pipeline works until the data changes shape.

An agent pipeline is especially exposed to this because some steps take input from outside: APIs, scraped pages, model output. Model output is the worst case, since it's free text that your code parses into fields.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/08-state-drift/fixed.py) does two things.

**It gives the state a contract and checks it after every step.**

```python
STATE_SCHEMA = {"subtotal": int, "fees": int, "total": int}

class StateDriftError(Exception):
    """A step violated the state contract."""

def validate_state(state, step_name):
    for key, expected in STATE_SCHEMA.items():
        if key in state and not isinstance(state[key], expected):
            raise StateDriftError(
                f"after step {step_name!r}: {key}={state[key]!r} is "
                f"{type(state[key]).__name__}, expected {expected.__name__}")
```

**It runs each step on a copy, and keeps an audit trail.**

```python
for step in steps:
    state = step(copy.deepcopy(state), order)
    validate_state(state, step.__name__)
    audit.append({"step": step.__name__, "state": copy.deepcopy(state)})
```

The step also changed. `enrich_with_fees` now coerces at the boundary: `state["fees"] = int(order["fee_api_response"])`. The string stops being a string the moment it enters the system.

Run it:

```text
invoice total: 1250
         parse_order: {'subtotal': 1200}
    enrich_with_fees: {'subtotal': 1200, 'fees': 50}
       compute_total: {'subtotal': 1200, 'fees': 50, 'total': 1250}
```

The audit trail shows the state after each step. If some future step writes `fees` as a string again, the error names the step: `after step 'enrich_with_fees': fees='50' is str, expected int`. That's the payoff. The step that corrupts state is the step named in the stack trace, so you skip the three-day archaeology.

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/08-state-drift/tests/test_fixed.py):

- `test_fixed_computes_correct_total` checks the answer is 1250.
- `test_fixed_catches_corrupting_step_by_name` swaps in a step that writes a string and checks the error names it.
- `test_fixed_keeps_audit_trail` checks the per-step snapshots exist.
- `test_broken_silently_corrupts_the_invoice` pins the original wrong total.

## Where the fix stops

- **`isinstance` is a weak schema.** In Python, `True` is an `int`, so a boolean passes the `int` check. A real contract uses a validation library, such as Pydantic or `dataclasses` with strict checks, which also covers ranges, required keys and unknown keys.
- **Money in integers is a simplification.** The demo uses whole numbers. Real money needs `Decimal` or integer cents, and a decision about rounding.
- **Only declared keys are checked.** The loop skips keys that aren't in `STATE_SCHEMA`, and skips schema keys that haven't been written yet. A step that adds a surprise key, or never writes a required one, gets through.
- **The audit trail is memory-only.** It lives in the returned dictionary. Write it to a log or a store if you want to debug a failure after the process is gone.
- **Deep copies cost something.** Copying state for every step is cheap for a dictionary this size. It stops being cheap for large payloads.

## The takeaway

State needs a contract, and every step's output gets validated against it. Coerce at the boundary where data enters, check after every step, and make sure the step that breaks the contract is the one that gets blamed.

---

[&larr; Previous: Failure 7]({{ '/failures/07-context-collapse/' | relative_url }}) · [Next: Failure 9, the amnesia bug &rarr;]({{ '/failures/09-amnesia-bug/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
