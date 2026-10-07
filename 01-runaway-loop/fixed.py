"""Failure #1 — The Runaway Loop (FIXED).

Same agent — with three stop conditions the model cannot override:
an iteration cap, a token budget, and a wall-clock timeout.

Run: python fixed.py   (safe: mock model unless ANTHROPIC_API_KEY is set)
"""
import os
import time

TASK = "Summarize the quarterly report. Reply with the word DONE when finished."

MAX_STEPS = 10          # hard iteration cap
TOKEN_BUDGET = 4_000    # rough token ceiling
TIMEOUT_SECONDS = 60    # wall-clock kill switch


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    step = sum(1 for m in messages if m["role"] == "assistant")
    return f"Draft {step + 1}: still refining the summary, one more pass..."


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL, max_steps=MAX_STEPS,
              token_budget=TOKEN_BUDGET, timeout=TIMEOUT_SECONDS):
    messages = [{"role": "user", "content": task}]
    tokens_burned = 0
    started = time.monotonic()
    log = []  # every step logged — you can see what it was thinking when cut off

    # THE FIX: stop conditions live OUTSIDE the model's judgment.
    for step in range(1, max_steps + 1):
        reply = model(messages)
        tokens_burned += len(reply.split()) * 2
        log.append({"step": step, "tokens": tokens_burned, "reply": reply})
        messages.append({"role": "assistant", "content": reply})

        if "DONE" in reply:
            return {"answer": reply, "stopped_by": "model", "steps": step, "log": log}
        if tokens_burned >= token_budget:
            return {"answer": None, "stopped_by": "token_budget", "steps": step, "log": log}
        if time.monotonic() - started >= timeout:
            return {"answer": None, "stopped_by": "timeout", "steps": step, "log": log}

        messages.append({"role": "user", "content": "Continue. Reply DONE when finished."})

    return {"answer": None, "stopped_by": "max_steps", "steps": max_steps, "log": log}


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"\nstopped_by={result['stopped_by']} after {result['steps']} steps")
    for entry in result["log"]:
        print(f"  step={entry['step']} tokens~{entry['tokens']}  {entry['reply'][:60]}")
