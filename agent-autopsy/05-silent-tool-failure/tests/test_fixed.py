"""Failure #5 — tests."""
import importlib.util
from pathlib import Path

import pytest


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson05_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def failing_fetch(url):
    return {"status": 500, "body": "<html>500 Internal Server Error</html>"}


def healthy_fetch(url):
    return {"status": 200, "body": "Q3 sales: $1.2M, up 8% QoQ."}


def summarizer(messages):
    return "Summary of: " + messages[0]["content"][-40:]


def test_fixed_surfaces_tool_failure():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=summarizer, fetch=failing_fetch)
    assert result["ok"] is False
    assert result["summary"] is None
    assert "HTTP 500" in result["error"]


def test_fixed_checked_fetch_raises():
    fixed = load("fixed")
    with pytest.raises(fixed.ToolFailure, match="HTTP 500"):
        fixed.checked_fetch("https://x", fetch=failing_fetch)


def test_fixed_still_works_when_tool_is_healthy():
    fixed = load("fixed")
    result = fixed.run_agent("task", model=summarizer, fetch=healthy_fetch)
    assert result["ok"] is True
    assert "1.2M" in result["summary"] or "Summary" in result["summary"]


def test_broken_reports_success_on_garbage():
    """Broken agent summarizes an error page and calls it a win."""
    broken = load("broken")
    result = broken.run_agent("task", model=summarizer, fetch=failing_fetch)
    assert result["ok"] is True                      # claims success
    assert "500 Internal Server Error" in result["summary"]  # built on garbage
