"""Failure #12 — tests."""
import importlib.util
from pathlib import Path


def load(name):
    path = Path(__file__).resolve().parent.parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lesson12_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PLAN = [("archive_report", "q3-sales"),
        ("delete_customer_records", "stale")]


def fresh_db():
    return {"customers": ["ana", "bo", "cy"], "archive": []}


def test_fixed_blocks_irreversible_without_approval():
    fixed = load("fixed")
    db = fresh_db()
    outcome = fixed.run_agent(PLAN, db=db)
    assert db["customers"] == ["ana", "bo", "cy"]  # nothing destroyed
    assert any("HELD FOR APPROVAL" in r for r in outcome["results"])


def test_fixed_still_runs_reversible_actions():
    fixed = load("fixed")
    db = fresh_db()
    fixed.run_agent(PLAN, db=db)
    assert db["archive"] == ["q3-sales"]  # reversible work proceeded


def test_fixed_executes_with_human_approval():
    fixed = load("fixed")
    db = fresh_db()
    seen = []

    def approver(request):
        seen.append(request)
        return True

    fixed.run_agent(PLAN, db=db, approve=approver)
    assert db["customers"] == []                      # human said yes
    assert "would affect" in seen[0]["impact"]        # decided with context


def test_fixed_respects_human_denial():
    fixed = load("fixed")
    db = fresh_db()
    fixed.run_agent(PLAN, db=db, approve=lambda req: False)
    assert db["customers"] == ["ana", "bo", "cy"]


def test_fixed_audits_every_decision():
    fixed = load("fixed")
    outcome = fixed.run_agent(PLAN, db=fresh_db())
    assert [a["status"] for a in outcome["audit"]] == \
        ["auto (reversible)", "BLOCKED — needs human"]


def test_broken_destroys_data_unprompted():
    """Broken agent deletes the customer table because it felt stale."""
    broken = load("broken")
    db = fresh_db()
    broken.run_agent(PLAN, db=db)
    assert db["customers"] == []  # gone. no human ever saw it coming.
