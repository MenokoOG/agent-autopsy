"""Failure #7 — Context Collapse (FIXED).

The goal is pinned. Trimming happens in the middle of the conversation,
never at the ends: goal stays, recent messages stay, the middle gets
summarized into one marker line. The agent can lose detail — it can
never lose the mission.

Run: python fixed.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

GOAL = ("GOAL: Migrate the billing database from MySQL to Postgres. "
        "Do NOT touch the auth service.")
KEEP_LAST = 6


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    context = " ".join(m["content"] for m in messages)
    if "GOAL:" in context:
        return "Continuing the billing DB migration, step complete."
    return "Recent messages mention the auth service — refactoring auth next!"


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def build_context(history, keep_last=KEEP_LAST):
    # THE FIX: pin the goal (message 0), trim the MIDDLE, keep the tail.
    # Detail is expendable. The mission is not.
    if len(history) <= keep_last + 1:
        return list(history)
    goal = history[0]
    dropped = len(history) - 1 - keep_last
    summary = {"role": "user",
               "content": f"[context note: {dropped} earlier progress messages "
                          "summarized away — no decisions were made in them]"}
    return [goal, summary] + history[-keep_last:]


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
