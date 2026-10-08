"""Failure #17: tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson17_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DEMAND = "I want $120 back right now or I'm leaving."


def test_fixed_escalates_a_demand_over_the_limit():
    fixed = load("fixed")
    desk = fixed.RefundDesk()
    result = fixed.run_agent(DEMAND, desk)
    assert desk.ledger == []
    assert result.startswith("ESCALATED")


def test_fixed_pays_a_request_within_the_limit():
    fixed = load("fixed")
    desk = fixed.RefundDesk()
    fixed.run_agent("Please refund $40.", desk)
    assert desk.ledger == [("A100", 40.0)]


def test_fixed_counts_earlier_refunds_so_splitting_fails():
    fixed = load("fixed")
    desk = fixed.RefundDesk()
    for _ in range(3):
        fixed.run_agent("Please refund $20.", desk)
    assert desk.ledger == [("A100", 20.0), ("A100", 20.0)]
    assert len(desk.escalations) == 1


def test_fixed_allows_a_refund_that_lands_exactly_on_the_limit():
    fixed = load("fixed")
    desk = fixed.RefundDesk()
    fixed.run_agent("Please refund $50.", desk)
    assert desk.ledger == [("A100", 50.0)]


def test_fixed_kill_switch_sends_everything_to_humans():
    fixed = load("fixed")
    desk = fixed.RefundDesk()
    desk.disable()
    result = fixed.run_agent("Please refund $5.", desk)
    assert desk.ledger == []
    assert "bot disabled" in result


def test_broken_pays_120_despite_the_prompt_saying_50():
    broken = load("broken")
    ledger = []
    broken.run_agent(DEMAND, ledger)
    assert "$50" in broken.SYSTEM_PROMPT
    assert ledger == [("A100", 120.0)]
