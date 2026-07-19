"""Failure #2 — The Stuck Agent (BROKEN).

The agent finished the work on step one. It just can't recognize it.
A brittle done-check keeps it "verifying" until the step cap burns out,
and it returns nothing — with the answer sitting right there in the log.

Run: python broken.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

TASK = "What is the capital of France? Reply TASK_COMPLETE when done."
MAX_STEPS = 20  # a cap exists (lesson #1 learned) — but the done-check is broken


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    # The model answers correctly and clearly says it's finished —
    # in natural language, like models do.
    return "The task is complete. The capital of France is Paris."


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL, max_steps=MAX_STEPS):
    messages = [{"role": "user", "content": task}]

    for step in range(1, max_steps + 1):
        reply = model(messages)
        print(f"step={step}  {reply[:70]}")
        messages.append({"role": "assistant", "content": reply})

        # THE BUG: exact-string equality on a free-form model reply.
        # "The task is complete." != "TASK_COMPLETE", so this never fires.
        if reply.strip() == "TASK_COMPLETE":
            return {"answer": reply, "steps": step}

        messages.append({"role": "user", "content": "Not done yet? Keep going."})

    return {"answer": None, "steps": max_steps}  # gave up holding the answer


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"\nanswer={result['answer']!r} after {result['steps']} steps")
