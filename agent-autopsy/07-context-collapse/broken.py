"""Failure #7 — Context Collapse (BROKEN).

Thirty steps in, the context window fills up. The trimming code keeps
"the most recent messages" — and quietly throws away the original goal.
The agent keeps working, diligently, on whatever the last few messages
happen to be about.

Run: python broken.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

GOAL = ("GOAL: Migrate the billing database from MySQL to Postgres. "
        "Do NOT touch the auth service.")
KEEP_LAST = 6  # naive context cap


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    # A model only knows what's in its context. If the goal isn't there,
    # it steers by whatever IS there — the most recent chatter.
    context = " ".join(m["content"] for m in messages)
    if "GOAL:" in context:
        return "Continuing the billing DB migration, step complete."
    return "Recent messages mention the auth service — refactoring auth next!"


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def build_context(history, keep_last=KEEP_LAST):
    # THE BUG: "keep the last N" treats the goal like any other message.
    # Message 0 — the mission — is the first thing trimmed.
    return history[-keep_last:]


def run_agent(goal, steps, model=MODEL):
    history = [{"role": "user", "content": goal}]
    for step in range(steps):
        history.append({"role": "user",
                        "content": f"Progress note {step}: checked a table, "
                                   "auth service logs look noisy btw."})
        reply = model(build_context(history))
        history.append({"role": "assistant", "content": reply})
    return {"final_reply": reply, "context": build_context(history)}


if __name__ == "__main__":
    result = run_agent(GOAL, steps=10)
    print(f"final reply: {result['final_reply']}")
    goal_present = any("GOAL:" in m["content"] for m in result["context"])
    print(f"goal still in context: {goal_present}")
