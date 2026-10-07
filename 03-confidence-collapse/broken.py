"""Failure #3 — Confidence Collapse (BROKEN).

The agent gets the right answer, then asks itself "are you sure?" — forever.
Each re-check flips the answer. It oscillates until the cap trips, burns 20x
the tokens the task needed, and returns whichever answer the parity landed on.

Run: python broken.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

TASK = "What is the capital of Australia?"
MAX_STEPS = 20


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    # Every "double-check" prompt makes the mock flip-flop, the way real
    # models waffle when you keep asking "are you absolutely sure?"
    checks = sum(1 for m in messages if "sure" in m["content"].lower())
    return "Canberra" if checks % 2 == 0 else "Hmm, actually it might be Sydney"


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL, max_steps=MAX_STEPS):
    messages = [{"role": "user", "content": task}]
    answer = None

    # THE BUG: unbounded self-verification. Every answer triggers another
    # "are you sure?" — and nothing ever counts as verified.
    for step in range(1, max_steps + 1):
        reply = model(messages)
        print(f"step={step}  {reply[:60]}")
        answer = reply
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user",
                         "content": "Are you absolutely sure? Double-check and answer again."})

    return {"answer": answer, "steps": max_steps, "model_calls": max_steps}


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"\nfinal answer after {result['model_calls']} calls: {result['answer']!r}")
