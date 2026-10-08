"""Failure #16: tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson16_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_fixed_stays_quiet_while_the_model_works():
    fixed = load("fixed")
    for week in (1, 2, 3):
        assert fixed.monitor(fixed.weekly_stats(fixed.make_week(week)))["alert"] is False


def test_fixed_alerts_when_recall_drops_even_though_accuracy_is_high():
    fixed = load("fixed")
    stats = fixed.weekly_stats(fixed.make_week(5))
    assert stats["accuracy"] >= 0.985
    assert stats["recall"] == 0.5
    assert fixed.monitor(stats)["alert"] is True


def test_fixed_alert_names_an_owner_and_a_first_action():
    fixed = load("fixed")
    result = fixed.monitor(fixed.weekly_stats(fixed.make_week(8)))
    assert result["owner"] == "fraud-ops"
    assert "manual review" in result["action"]


def test_fixed_refuses_a_monitor_with_no_owner():
    fixed = load("fixed")
    try:
        fixed.MonitorConfig(metric="recall", min_value=0.9, owner=" ", action="page")
    except ValueError:
        return
    raise AssertionError("accepted a monitor with no owner")


def test_fixed_first_alert_is_week_four():
    fixed = load("fixed")
    alerts = [fixed.monitor(fixed.weekly_stats(fixed.make_week(w)))["alert"]
              for w in range(1, 9)]
    assert alerts.index(True) == 3  # week 4, when the first 5 fraud cases slip


def test_broken_never_alerts_while_every_fraud_case_is_missed():
    """Week 7 misses all 20 fraud cases and accuracy is still 98%."""
    broken = load("broken")
    stats = broken.weekly_stats(broken.make_week(7))
    assert stats["caught"] == 0
    assert round(stats["accuracy"], 2) == 0.98
    assert broken.monitor(stats) is False
