"""Failure #4 — tests."""
import importlib.util
import json
from pathlib import Path

import pytest


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson04_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hallucinate_then_recover(messages, tools):
    corrected = any("Unknown tool" in m["content"] for m in messages)
    if corrected:
        return json.dumps({"tool": "web_search", "args": {"query": "active users"}})
    return json.dumps({"tool": "database_query", "args": {"sql": "SELECT 1"}})


def always_hallucinate(messages, tools):
    return json.dumps({"tool": "database_query", "args": {"sql": "SELECT 1"}})


def test_fixed_corrects_hallucinated_tool():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=hallucinate_then_recover)
    assert result["tool"] == "web_search"
    assert result["attempts"] == ["database_query", "web_search"]


def test_fixed_fails_loud_when_model_never_recovers():
    fixed = load("fixed")
    with pytest.raises(RuntimeError, match="No valid tool"):
        fixed.run_agent("task", model=always_hallucinate, max_retries=3)


def test_fixed_executes_valid_request_first_try():
    fixed = load("fixed")

    def sane(messages, tools):
        return json.dumps({"tool": "calculator", "args": {"expression": "2+2"}})

    result = fixed.run_agent("task", model=sane)
    assert result["result"] == "4"
    assert result["attempts"] == ["calculator"]


def test_broken_crashes_on_hallucinated_tool():
    """Broken agent executes whatever name the model dreams up — KeyError."""
    broken = load("broken")
    with pytest.raises(KeyError):
        broken.run_agent("task", model=always_hallucinate)
