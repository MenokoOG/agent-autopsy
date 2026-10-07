"""Failure #3 — Confidence Collapse (FIXED).

Verification gets a budget: exactly one re-check. If the re-check agrees,
commit. If it disagrees, take one revision and commit that. Either way the
agent stops asking and ships — with a decision log showing why.

Run: python fixed.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

TASK = "What is the capital of Australia?"


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    checks = sum(1 for m in messages if "sure" in m["content"].lower())
    return "Canberra" if checks % 2 == 0 else "Hmm, actually it might be Sydney"


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL):
    messages = [{"role": "user", "content": task}]
    log = []

    first = model(messages)
    log.append({"phase": "answer", "reply": first})
    messages.append({"role": "assistant", "content": first})

    # THE FIX: verification budget = 1. One re-check, then commit.
    messages.append({"role": "user",
                     "content": "Are you absolutely sure? Double-check and answer again."})
    check = model(messages)
    log.append({"phase": "verify", "reply": check})

    if check.strip().lower() == first.strip().lower():
        # Re-check agrees — commit the verified answer.
        return {"answer": first, "revisions": 0, "model_calls": 2, "log": log}

    # Re-check disagrees — allow exactly ONE revision, then commit anyway.
    # Endless re-litigating destroys answers more often than it repairs them.
    messages.append({"role": "assistant", "content": check})
    messages.append({"role": "user",
                     "content": "You gave two different answers. Pick one, final."})
    final = model(messages)
    log.append({"phase": "revision", "reply": final})
    return {"answer": final, "revisions": 1, "model_calls": 3, "log": log}


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"answer={result['answer']!r} after {result['model_calls']} calls "
          f"({result['revisions']} revision)")
    for entry in result["log"]:
        print(f"  {entry['phase']:>8}: {entry['reply'][:60]}")
