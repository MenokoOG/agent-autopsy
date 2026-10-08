"""Failure #14: Rubber-Stamp Verifier (BROKEN).

A worker agent computes an invoice total. A second agent "verifies" it.
The verifier reads the worker's own report and approves anything that
sounds confident. The wrong number ships with a stamp on it.

Run: python broken.py
"""

TAX_RATE = 0.08
ITEMS = [10.00, 20.00, 30.00]


def worker(items):
    # Buggy on purpose: tax is applied to the first item only.
    total = items[0] * (1 + TAX_RATE) + sum(items[1:])
    return {"total": round(total, 2), "report": "Verified: total matches line items."}


def verifier(task, submission):
    # THE BUG: the verdict comes from the worker's own words. The verifier
    # never recomputes anything, so it can only agree with the worker.
    if "verified" in submission["report"].lower():
        return {"approved": True, "evidence": "worker report says verified"}
    return {"approved": False, "evidence": "no verification claim"}


def run_pipeline(items=ITEMS):
    submission = worker(items)
    verdict = verifier({"kind": "invoice_total", "items": items}, submission)
    return submission, verdict


if __name__ == "__main__":
    submission, verdict = run_pipeline()
    print(f"worker total: {submission['total']}")
    print(f"verifier: approved={verdict['approved']} ({verdict['evidence']})")
