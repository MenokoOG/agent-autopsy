"""Failure #6: tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson06_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def echo_model(messages):
    return messages[-1]["content"]


def test_fixed_routes_math_to_calculator():
    fixed = load("fixed")
    result = fixed.run_agent("What is 12.5% of 3,847?", model=echo_model)
    assert result["tool"] == "calculator"
    assert abs(float(result["answer"]) - 480.875) < 1e-9


def test_fixed_routes_plain_arithmetic():
    fixed = load("fixed")
    result = fixed.run_agent("Compute 240 * 12 + 7", model=echo_model)
    assert result["tool"] == "calculator"
    assert float(result["answer"]) == 2887.0


def test_fixed_still_searches_for_facts():
    fixed = load("fixed")
    result = fixed.run_agent("Who is the CEO of Anthropic?", model=echo_model)
    assert result["tool"] == "web_search"


def test_broken_searches_for_math_and_gets_it_wrong():
    """Broken agent asks the internet to do arithmetic. It obliges, wrongly."""
    broken = load("broken")
    result = broken.run_agent("What is 12.5% of 3,847?", model=echo_model)
    assert result["tool"] == "web_search"
    assert "480.875" not in result["answer"]  # stale forum answer, not math


def test_calculator_does_arithmetic():
    fixed = load("fixed")
    assert float(fixed.calculator("240 * 12 + 7")) == 2887.0
    assert float(fixed.calculator("-(3 + 4) % 5")) == 3.0


def test_calculator_rejects_code():
    fixed = load("fixed")
    for bad in ["__import__('os').getcwd()", "(1).__class__", "2 ** 99999999", "abs(-1)"]:
        try:
            fixed.calculator(bad)
        except (ValueError, SyntaxError):
            continue
        raise AssertionError(f"accepted: {bad}")
