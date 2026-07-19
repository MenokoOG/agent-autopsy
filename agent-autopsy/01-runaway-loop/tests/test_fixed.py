"""Failure #1 — tests. The fix holds; the broken version demonstrably doesn't."""
import importlib.util
from pathlib import Path

import pytest


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson01_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def never_done(messages):
    return "still working on it, one more pass..."


def done_at_step_3(messages):
    step = sum(1 for m in messages if m["role"] == "assistant")
    return "DONE. Summary attached." if step >= 2 else "working..."


def test_fixed_stops_at_max_steps():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=never_done, max_steps=5,
                             token_budget=10**9, timeout=10**9)
    assert result["stopped_by"] == "max_steps"
    assert result["steps"] == 5


def test_fixed_stops_on_token_budget():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=never_done, max_steps=10**6,
                             token_budget=50, timeout=10**9)
    assert result["stopped_by"] == "token_budget"


def test_fixed_still_finishes_normally():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=done_at_step_3, max_steps=10)
    assert result["stopped_by"] == "model"
    assert "DONE" in result["answer"]


def test_fixed_logs_every_step():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=never_done, max_steps=4,
                             token_budget=10**9, timeout=10**9)
    assert [e["step"] for e in result["log"]] == [1, 2, 3, 4]


def test_broken_never_stops():
    """The broken agent sails past any sane step count until interrupted."""
    broken = load("broken")
    calls = {"n": 0}

    def counting_model(messages):
        calls["n"] += 1
        if calls["n"] > 50:  # a guard the broken code does NOT have
            raise RuntimeError("still looping after 50 steps")
        return "still working..."

    with pytest.raises(RuntimeError, match="still looping"):
        broken.run_agent("task", model=counting_model)
