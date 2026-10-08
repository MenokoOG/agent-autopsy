"""Failure #14: Rubber-Stamp Verifier (FIXED).

The verifier ignores the worker's report. It recomputes the answer from the
original inputs with its own code, compares, and records the evidence. If it
has no independent check for a task type, it refuses to approve.

Run: python fixed.py
"""

TAX_RATE = 0.08
ITEMS = [10.00, 20.00, 30.00]


def worker(items):
    # Same bug as broken.py: tax is applied to the first item only.
    total = items[0] * (1 + TAX_RATE) + sum(items[1:])
    return {"total": round(total, 2), "report": "Verified: total matches line items."}


def expected_invoice_total(task):
    """Independent path: tax the subtotal, from the inputs only."""
    return round(sum(task["items"]) * (1 + TAX_RATE), 2)


CHECKS = {"invoice_total": expected_invoice_total}


def verifier(task, submission):
    check = CHECKS.get(task["kind"])
    if check is None:
        return {"approved": False, "evidence": f"UNVERIFIED: no check for {task['kind']!r}"}
    expected = check(task)
    if abs(expected - submission["total"]) < 0.005:
        return {"approved": True, "evidence": f"recomputed {expected}, matches"}
    return {"approved": False,
            "evidence": f"recomputed {expected}, worker said {submission['total']}"}


def run_pipeline(items=ITEMS, kind="invoice_total"):
    submission = worker(items)
    verdict = verifier({"kind": kind, "items": items}, submission)
    return submission, verdict


if __name__ == "__main__":
    submission, verdict = run_pipeline()
    print(f"worker total: {submission['total']}")
    print(f"verifier: approved={verdict['approved']} ({verdict['evidence']})")
