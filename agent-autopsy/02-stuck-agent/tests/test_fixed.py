"""Failure #2 — tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson02_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def natural_completion(messages):
    return "The task is complete. The capital of France is Paris."


def test_fixed_recognizes_natural_language_completion():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=natural_completion)
    assert result["steps"] == 1
    assert "Paris" in result["answer"]


def test_fixed_stall_detector_catches_repeats():
    fixed = load("fixed")
    replies = iter(["Working on it.", "Same answer: Paris.", "Same answer: Paris."])

    def repeating(messages):
        return next(replies)

    result = fixed.run_agent("task", model=repeating)
    assert result["stopped_by"] == "stall"
    assert "Paris" in result["answer"]


def test_fixed_accepts_marker_variants():
    fixed = load("fixed")
    for reply in ["TASK_COMPLETE", "status: complete — Paris", "Task complete!"]:
        assert fixed.is_complete(reply), reply


def test_broken_burns_all_steps_holding_the_answer():
    """Broken agent has the answer at step 1 and still returns None."""
    broken = load("broken")
    result = broken.run_agent("task", model=natural_completion, max_steps=8)
    assert result["answer"] is None
    assert result["steps"] == 8
