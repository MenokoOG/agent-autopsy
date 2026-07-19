"""Failure #7 — tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson07_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_history(n):
    history = [{"role": "user", "content": "GOAL: migrate billing DB"}]
    for i in range(n):
        history.append({"role": "user", "content": f"note {i}"})
    return history


def test_fixed_pins_goal_after_heavy_trimming():
    fixed = load("fixed")
    context = fixed.build_context(make_history(50), keep_last=6)
    assert "GOAL:" in context[0]["content"]


def test_fixed_context_stays_bounded():
    fixed = load("fixed")
    context = fixed.build_context(make_history(500), keep_last=6)
    assert len(context) <= 8  # goal + summary marker + last 6


def test_fixed_keeps_most_recent_messages():
    fixed = load("fixed")
    context = fixed.build_context(make_history(50), keep_last=6)
    assert context[-1]["content"] == "note 49"


def test_fixed_agent_stays_on_mission():
    fixed = load("fixed")
    result = fixed.run_agent("GOAL: migrate billing DB", steps=12,
                             model=fixed.mock_model)
    assert "migration" in result["final_reply"]


def test_broken_loses_the_goal():
    """Broken trim drops message 0 — the mission — and the agent drifts."""
    broken = load("broken")
    context = broken.build_context(make_history(50), keep_last=6)
    assert not any("GOAL:" in m["content"] for m in context)

    result = broken.run_agent("GOAL: migrate billing DB", steps=12,
                              model=broken.mock_model)
    assert "auth" in result["final_reply"]  # drifted to the wrong task
