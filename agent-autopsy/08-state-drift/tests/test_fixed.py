"""Failure #8 — tests."""
import importlib.util
from pathlib import Path

import pytest


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson08_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_fixed_computes_correct_total():
    fixed = load("fixed")
    result = fixed.run_pipeline({"items": [400, 800], "fee_api_response": "50"})
    assert result["total"] == 1250


def test_fixed_catches_corrupting_step_by_name():
    fixed = load("fixed")

    def rogue_step(state, order):
        state["total"] = "oops-a-string"
        return state

    with pytest.raises(fixed.StateDriftError, match="rogue_step"):
        fixed.run_pipeline({"items": [1], "fee_api_response": "0"},
                           steps=[fixed.parse_order, rogue_step])


def test_fixed_keeps_audit_trail():
    fixed = load("fixed")
    result = fixed.run_pipeline({"items": [400, 800], "fee_api_response": "50"})
    steps = [e["step"] for e in result["audit"]]
    assert steps == ["parse_order", "enrich_with_fees", "compute_total"]


def test_broken_silently_corrupts_the_invoice():
    """Broken pipeline concatenates strings and calls it a total."""
    broken = load("broken")
    result = broken.run_pipeline({"items": [400, 800], "fee_api_response": "50"})
    assert result["total"] == "120050"  # silent corruption, no exception
