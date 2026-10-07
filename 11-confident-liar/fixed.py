"""Failure #11 — The Confident Liar (FIXED).

Grounding is enforced in code, not requested in the prompt. Every factual
claim must cite an evidence ID from actual tool results. No evidence?
The only legal answer is "I don't know" — and the code guarantees it.

Run: python fixed.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os
import re

TASK = "What was ACME Corp's Q3 2025 revenue?"


def search(query):
    return []


def real_model(prompt):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text


def mock_model(prompt):
    return ("ACME Corp reported Q3 2025 revenue of $4.21 billion, up 12% "
            "year-over-year (source: ACME investor relations).")


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model

NO_DATA_ANSWER = ("I could not verify this. My search returned no results for "
                  "ACME Corp Q3 2025 revenue, so I won't state a figure.")


def contains_specific_claims(answer):
    # Numbers, dollar amounts, percentages — the things liars are made of.
    return bool(re.search(r"[\$€£]?\d[\d,.]*\s*(billion|million|%|percent)?",
                          answer, re.IGNORECASE))


def run_agent(task, model=MODEL, search_tool=search):
    evidence = search_tool(task)

    # THE FIX (gate 1): no evidence, no factual answer. Don't even ask the
    # model — an honest "I don't know" is computed, not generated.
    if not evidence:
        return {"answer": NO_DATA_ANSWER, "evidence": [], "grounded": False}

    numbered = "\n".join(f"[{i}] {e}" for i, e in enumerate(evidence))
    prompt = (f"{task}\n\nEvidence:\n{numbered}\n\n"
              "Answer using ONLY the evidence above. Cite [n] for every claim. "
              "If the evidence doesn't contain the answer, say so.")
    answer = model(prompt)

    # THE FIX (gate 2): specific claims with no citation get rejected.
    if contains_specific_claims(answer) and not re.search(r"\[\d+\]", answer):
        return {"answer": NO_DATA_ANSWER, "evidence": evidence, "grounded": False}

    return {"answer": answer, "evidence": evidence, "grounded": True}


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"grounded: {result['grounded']}")
    print(f"answer:   {result['answer']}")
