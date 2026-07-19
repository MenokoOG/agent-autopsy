"""Failure #2 — The Stuck Agent (FIXED).

Two changes: a completion signal parsed robustly instead of by exact
equality, and a stall detector — if the agent repeats itself, it is done
whether it knows it or not.

Run: python fixed.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os
import re

TASK = "What is the capital of France? End your reply with STATUS: COMPLETE when done."
MAX_STEPS = 20


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    return "The task is complete. The capital of France is Paris."


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def is_complete(reply):
    # THE FIX (part 1): parse the signal tolerantly — regex, not equality.
    # Catches TASK_COMPLETE, "Status: complete", "The task is complete." etc.
    return bool(re.search(r"(task|status)[\W_]*(is[\W_]*)?complete", reply, re.IGNORECASE))


def run_agent(task, model=MODEL, max_steps=MAX_STEPS):
    messages = [{"role": "user", "content": task}]
    previous_reply = None

    for step in range(1, max_steps + 1):
        reply = model(messages)
        messages.append({"role": "assistant", "content": reply})

        if is_complete(reply):
            return {"answer": reply, "steps": step, "stopped_by": "signal"}

        # THE FIX (part 2): stall detection. Two identical replies in a row
        # means no progress is being made — take the answer and stop.
        if reply == previous_reply:
            return {"answer": reply, "steps": step, "stopped_by": "stall"}
        previous_reply = reply

        messages.append({"role": "user", "content": "Not done yet? Keep going."})

    return {"answer": previous_reply, "steps": max_steps, "stopped_by": "max_steps"}


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"stopped_by={result['stopped_by']} steps={result['steps']}")
    print(f"answer={result['answer']!r}")
