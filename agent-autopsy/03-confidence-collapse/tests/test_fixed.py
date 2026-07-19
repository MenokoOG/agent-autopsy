"""Failure #3 — tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson03_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_oscillator():
    replies = {"n": 0}

    def model(messages):
        replies["n"] += 1
        return "Canberra" if replies["n"] % 2 == 1 else "Actually, maybe Sydney"

    return model, replies


def stable_model(messages):
    return "Canberra"


def test_fixed_commits_when_verify_agrees():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=stable_model)
    assert result["answer"] == "Canberra"
    assert result["revisions"] == 0
    assert result["model_calls"] == 2


def test_fixed_caps_revisions_at_one():
    fixed = load("fixed")
    model, _ = make_oscillator()
    result = fixed.run_agent("task", model=model)
    assert result["revisions"] == 1
    assert result["model_calls"] == 3  # answer + verify + one revision, done


def test_fixed_keeps_decision_log():
    fixed = load("fixed")
    model, _ = make_oscillator()
    result = fixed.run_agent("task", model=model)
    assert [e["phase"] for e in result["log"]] == ["answer", "verify", "revision"]


def test_broken_burns_calls_oscillating():
    """Broken agent makes max_steps calls for a 1-call question."""
    broken = load("broken")
    model, counter = make_oscillator()
    result = broken.run_agent("task", model=model, max_steps=20)
    assert counter["n"] == 20  # 20 model calls to answer one question
    assert result["answer"] != "Canberra"  # parity landed on the waffle
