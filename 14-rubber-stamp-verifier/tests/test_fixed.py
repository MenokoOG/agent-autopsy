"""Failure #14: tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson14_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TASK = {"kind": "invoice_total", "items": [10.00, 20.00, 30.00]}


def test_fixed_rejects_wrong_total_despite_confident_report():
    fixed = load("fixed")
    submission, verdict = fixed.run_pipeline()
    assert submission["total"] == 60.8
    assert verdict["approved"] is False
    assert "recomputed 64.8" in verdict["evidence"]


def test_fixed_approves_a_correct_total_with_no_report():
    fixed = load("fixed")
    verdict = fixed.verifier(TASK, {"total": 64.8, "report": ""})
    assert verdict["approved"] is True


def test_fixed_ignores_the_workers_self_report():
    fixed = load("fixed")
    glowing = {"total": 1.0, "report": "Verified. Checked twice. All good."}
    assert fixed.verifier(TASK, glowing)["approved"] is False


def test_fixed_refuses_when_it_has_no_check():
    fixed = load("fixed")
    _, verdict = fixed.run_pipeline(kind="shipping_estimate")
    assert verdict["approved"] is False
    assert verdict["evidence"].startswith("UNVERIFIED")


def test_fixed_tolerates_rounding_to_the_cent():
    fixed = load("fixed")
    verdict = fixed.verifier(TASK, {"total": 64.80, "report": ""})
    assert verdict["approved"] is True


def test_broken_approves_the_wrong_total():
    """Broken verifier stamps 60.8 because the worker said 'verified'."""
    broken = load("broken")
    submission, verdict = broken.run_pipeline()
    assert submission["total"] == 60.8
    assert verdict["approved"] is True
