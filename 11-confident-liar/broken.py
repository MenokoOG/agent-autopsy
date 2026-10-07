"""Failure #11 — The Confident Liar (BROKEN).

The search tool comes back empty. The model, asked for revenue numbers it
does not have, produces beautiful, specific, wrong ones — with a fake
citation for garnish. The agent passes them straight to the user.

Run: python broken.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

TASK = "What was ACME Corp's Q3 2025 revenue?"


def search(query):
    return []  # no results. ACME is private; the number isn't out there.


def real_model(prompt):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text


def mock_model(prompt):
    # Models abhor a vacuum. Asked for a number with no data, this one
    # invents a plausible one — the way real models do under pressure.
    return ("ACME Corp reported Q3 2025 revenue of $4.21 billion, up 12% "
            "year-over-year (source: ACME investor relations).")


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL, search_tool=search):
    evidence = search_tool(task)

    # THE BUG: the answer never has to point at evidence. Empty search
    # results and a confident reply coexist just fine — and ship.
    prompt = f"{task}\n\nSearch results: {evidence}"
    return {"answer": model(prompt), "evidence": evidence}


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"evidence: {result['evidence']}")
    print(f"answer:   {result['answer']}")
