---
title: "Failure 14: Rubber-stamp verifier"
permalink: /failures/14-rubber-stamp-verifier/
---

# Failure 14: Rubber-stamp verifier

*The worker said "verified." The verifier believed it. The invoice total was $4.00 short.*

## The scenario

A worker agent computes an invoice total: three line items, 8% tax. A second agent checks the work before it goes out. On a diagram, the pipeline has a safety step. In the code, the checker reads the worker's own report, sees the word "verified" and approves.

Verification failures are a large group in the MAST study of multi-agent failures. The authors found that 23.5% of annotated failures fell under task verification: 8.2% had no or incomplete verification, and 9.1% had verification that ran and still missed the error ([Cemri et al., 2025](https://arxiv.org/abs/2503.13657)). Those are the study's numbers across 1,642 traces. The numbers in this article come from the demo code.

The code is in [`14-rubber-stamp-verifier`](https://github.com/MenokoOG/agent-autopsy/tree/main/14-rubber-stamp-verifier).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/14-rubber-stamp-verifier/broken.py):

```python
def worker(items):
    # Buggy on purpose: tax is applied to the first item only.
    total = items[0] * (1 + TAX_RATE) + sum(items[1:])
    return {"total": round(total, 2), "report": "Verified: total matches line items."}

def verifier(task, submission):
    # THE BUG: the verdict comes from the worker's own words.
    if "verified" in submission["report"].lower():
        return {"approved": True, "evidence": "worker report says verified"}
    return {"approved": False, "evidence": "no verification claim"}
```

The run:

```text
worker total: 60.8
verifier: approved=True (worker report says verified)
```

The correct total is 64.8. The verifier never computed it. Its evidence is a quote from the thing it was supposed to check.

## Why it happens

Verifying is hard to build, so it gets built last and thin. An LLM judge is easy to add and easy to fool. A judge that sees the worker's reasoning tends to agree with it, in the same way a reviewer who reads the author's explanation first tends to accept the diff. If the judge also shares the worker's model, prompts and blind spots, its errors line up with the worker's.

There's also a structural cause. The check was written to answer "did the worker finish?" and ended up answering "did the worker say it finished?"

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/14-rubber-stamp-verifier/fixed.py) changes three things.

**Recompute from the inputs.**

```python
def expected_invoice_total(task):
    """Independent path: tax the subtotal, from the inputs only."""
    return round(sum(task["items"]) * (1 + TAX_RATE), 2)
```

The verifier takes the original line items, not the worker's output, and gets to the answer by a different route. A bug in the worker's arithmetic doesn't carry over.

**Compare and keep the evidence.**

```python
expected = check(task)
if abs(expected - submission["total"]) < 0.005:
    return {"approved": True, "evidence": f"recomputed {expected}, matches"}
return {"approved": False,
        "evidence": f"recomputed {expected}, worker said {submission['total']}"}
```

The verdict carries numbers a person can check.

**No check, no approval.**

```python
check = CHECKS.get(task["kind"])
if check is None:
    return {"approved": False, "evidence": f"UNVERIFIED: no check for {task['kind']!r}"}
```

A task type with no independent check is rejected. The default answer is no.

Run it:

```text
worker total: 60.8
verifier: approved=False (recomputed 64.8, worker said 60.8)
```

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/14-rubber-stamp-verifier/tests/test_fixed.py):

- `test_fixed_rejects_wrong_total_despite_confident_report` checks the wrong total is caught and the evidence names 64.8.
- `test_fixed_approves_a_correct_total_with_no_report` checks the verdict doesn't depend on the report's wording.
- `test_fixed_ignores_the_workers_self_report` checks a glowing report can't rescue a wrong number.
- `test_fixed_refuses_when_it_has_no_check` checks the default for an unknown task type.
- `test_fixed_tolerates_rounding_to_the_cent` checks the comparison tolerance.
- `test_broken_approves_the_wrong_total` pins the original failure.

## Where the fix stops

- **Most work has no clean recomputation.** An invoice total has one right answer. A summary, a plan or a code change doesn't. For those, build the best independent evidence you can: run the tests the worker didn't write, check each citation against its source, validate against a schema. Treat "the judge model liked it" as the weakest form of evidence.
- **A second model isn't an independent check.** If the verifier is the same model with the same context, expect correlated mistakes. Give it different inputs, different tools or deterministic code.
- **The check can be wrong too.** The verifier's formula is code, so it needs its own tests. If both paths share a bug, the pipeline agrees on a wrong answer.
- **Tolerance hides small errors.** The half-cent window is fine for money. Pick tolerances on purpose for anything else.
- **Rejection needs a path.** The demo returns a verdict. A real pipeline decides what happens next: a bounded retry, a human review or a halt. See [failure 12]({{ '/failures/12-no-human-brake/' | relative_url }}).

## The takeaway

A verifier earns its place by producing its own evidence from the original inputs, and it rejects what it can't check.

---

[&larr; Previous: Failure 13]({{ '/failures/13-reasoning-action-mismatch/' | relative_url }}) · [Next: The field checklist &rarr;]({{ '/field-checklist/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
