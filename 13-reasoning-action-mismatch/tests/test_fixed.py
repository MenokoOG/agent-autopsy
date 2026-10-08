"""Failure #13: tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson13_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mismatched_step():
    return {
        "said": "Refunding $20.00 on A100.",
        "intent": {"order_id": "A100", "amount": 20.00},
        "do": {"order_id": "A101", "amount": 200.00},
    }


def matching_step():
    return {
        "said": "Refunding $20.00 on A100.",
        "intent": {"order_id": "A100", "amount": 20.00},
        "do": {"order_id": "A100", "amount": 20.00},
    }


def test_fixed_blocks_when_call_differs_from_intent():
    fixed = load("fixed")
    ledger = fixed.make_ledger()
    result = fixed.run_agent(mismatched_step(), ledger)
    assert ledger == []
    assert result.startswith("BLOCKED")


def test_fixed_runs_when_intent_matches_call():
    fixed = load("fixed")
    ledger = fixed.make_ledger()
    fixed.run_agent(matching_step(), ledger)
    assert ledger == [("A100", 20.00)]


def test_fixed_reports_every_differing_field():
    fixed = load("fixed")
    problems = fixed.diff_intent(
        {"order_id": "A100", "amount": 20.00},
        {"order_id": "A101", "amount": 200.00},
    )
    assert len(problems) == 2
    assert any(p.startswith("amount") for p in problems)


def test_fixed_blocks_an_extra_field_in_the_call():
    fixed = load("fixed")
    problems = fixed.diff_intent({"order_id": "A100"},
                                 {"order_id": "A100", "amount": 20.00})
    assert problems == ["amount: said None, did 20.0"]


def test_fixed_audits_blocked_and_executed():
    fixed = load("fixed")
    ledger, audit = fixed.make_ledger(), []
    fixed.run_agent(mismatched_step(), ledger, audit)
    fixed.run_agent(matching_step(), ledger, audit)
    assert [a["status"] for a in audit] == ["BLOCKED mismatch", "executed"]


def test_broken_refunds_the_wrong_order_while_saying_otherwise():
    """Broken agent tells the user A100 and pays out on A101."""
    broken = load("broken")
    ledger = broken.make_ledger()
    broken.run_agent(mismatched_step(), ledger)
    assert ledger == [("A101", 200.00)]
