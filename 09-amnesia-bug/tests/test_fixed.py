"""Failure #9 — tests."""
import importlib.util
from collections import Counter
from pathlib import Path

import pytest


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson09_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


USERS = ["ana@example.com", "bo@example.com", "cy@example.com"]


def test_fixed_no_duplicate_side_effects_after_crash(tmp_path):
    fixed = load("fixed")
    checkpoint = tmp_path / "checkpoint.jsonl"
    outbox = []

    with pytest.raises(fixed.TransientCrash):
        fixed.run_batch(USERS, outbox, checkpoint=checkpoint, crash_at=2)
    fixed.run_batch(USERS, outbox, checkpoint=checkpoint)

    assert Counter(outbox) == {u: 1 for u in USERS}  # each exactly once


def test_fixed_completes_all_items(tmp_path):
    fixed = load("fixed")
    checkpoint = tmp_path / "checkpoint.jsonl"
    outbox = []
    fixed.run_batch(USERS, outbox, checkpoint=checkpoint)
    assert outbox == USERS


def test_fixed_rerun_after_success_does_nothing(tmp_path):
    fixed = load("fixed")
    checkpoint = tmp_path / "checkpoint.jsonl"
    outbox = []
    fixed.run_batch(USERS, outbox, checkpoint=checkpoint)
    fixed.run_batch(USERS, outbox, checkpoint=checkpoint)  # idempotent rerun
    assert Counter(outbox) == {u: 1 for u in USERS}


def test_broken_duplicates_side_effects_after_crash():
    """Broken batch redoes finished work — customers get the email twice."""
    broken = load("broken")
    outbox = []
    with pytest.raises(broken.TransientCrash):
        broken.run_batch(USERS, outbox, crash_at=2)
    broken.run_batch(USERS, outbox)

    dupes = {u: n for u, n in Counter(outbox).items() if n > 1}
    assert dupes == {"ana@example.com": 2, "bo@example.com": 2}
