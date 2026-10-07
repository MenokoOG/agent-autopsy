"""Failure #11 — tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson11_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fabricator(prompt):
    return "Revenue was $4.21 billion, up 12% year-over-year."


def cited_answer(prompt):
    return "Revenue was $2.0 billion [0], up 5% [1]."


def test_fixed_refuses_without_evidence():
    fixed = load("fixed")
    result = fixed.run_agent("revenue?", model=fabricator, search_tool=lambda q: [])
    assert result["grounded"] is False
    assert "4.21" not in result["answer"]
    assert "could not verify" in result["answer"]


def test_fixed_rejects_uncited_specifics_even_with_evidence():
    fixed = load("fixed")
    evidence = ["ACME 10-Q filing: Q3 revenue $2.0B"]
    result = fixed.run_agent("revenue?", model=fabricator,
                             search_tool=lambda q: evidence)
    assert result["grounded"] is False  # numbers with no [n] citation


def test_fixed_accepts_cited_grounded_answer():
    fixed = load("fixed")
    evidence = ["ACME 10-Q: Q3 revenue $2.0B", "ACME PR: growth 5%"]
    result = fixed.run_agent("revenue?", model=cited_answer,
                             search_tool=lambda q: evidence)
    assert result["grounded"] is True
    assert "[0]" in result["answer"]


def test_broken_ships_the_fabrication():
    """Broken agent returns invented numbers on zero evidence."""
    broken = load("broken")
    result = broken.run_agent("revenue?", model=fabricator, search_tool=lambda q: [])
    assert result["evidence"] == []
    assert "$4.21 billion" in result["answer"]  # confident, specific, fake
