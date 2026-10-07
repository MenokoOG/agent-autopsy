"""Failure #1 — The Runaway Loop (BROKEN).

An agent loop with no external stop condition. The model is the only thing
deciding when to stop — and one day it never does.

Run: python broken.py
Uses a mock model unless ANTHROPIC_API_KEY is set. In mock mode this costs
nothing but WILL loop until you Ctrl+C. That is the lesson.
"""
import os

TASK = "Summarize the quarterly report. Reply with the word DONE when finished."


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    # Simulates the prod edge case: the model keeps "improving" its answer
    # and never emits the DONE signal.
    step = sum(1 for m in messages if m["role"] == "assistant")
    return f"Draft {step + 1}: still refining the summary, one more pass..."


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL):
    messages = [{"role": "user", "content": task}]
    tokens_burned = 0

    # THE BUG: `while True` with the model as the only exit. No iteration cap,
    # no token budget, no timeout. The agent decides when it's done — forever.
    while True:
        reply = model(messages)
        tokens_burned += len(reply.split()) * 2  # rough cost proxy
        print(f"step={len(messages) // 2 + 1}  tokens~{tokens_burned}  {reply[:60]}")
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": "Continue. Reply DONE when finished."})

        if "DONE" in reply:  # the model never says it
            return reply


if __name__ == "__main__":
    print("WARNING: no stop guard. Ctrl+C to escape.\n")
    run_agent(TASK)
