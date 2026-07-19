"""Failure #6 — Wrong Tool Pick (FIXED).

Routing is a decision, not a default. Classify what the task NEEDS —
exact computation vs. fresh external facts — and give the router an
explicit rule for each class. Deterministic first, model fallback second.

Run: python fixed.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os
import re

TASK = "What is 12.5% of 3,847?"


def calculator(expression):
    return str(eval(expression, {"__builtins__": {}}, {}))


def web_search(query):
    return "Top result (forum, 2019): '12.5% of 3,847 is about 480.'"


TOOLS = {"calculator": calculator, "web_search": web_search}


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    return messages[-1]["content"]


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def extract_math(task):
    """Turn 'What is 12.5% of 3,847?' into a computable expression."""
    m = re.search(r"([\d.,]+)\s*%\s*of\s*([\d.,]+)", task)
    if m:
        pct, base = (float(g.replace(",", "")) for g in m.groups())
        return f"{pct} / 100 * {base}"
    m = re.search(r"[\d.,]+(\s*[-+*/]\s*[\d.,]+)+", task)
    return m.group(0).replace(",", "") if m else None


def route(task):
    # THE FIX: route on what the task needs. Arithmetic needs exactness —
    # that's the calculator, every time. Search is for facts that live
    # outside the prompt, not for math.
    expression = extract_math(task)
    if expression:
        return "calculator", expression
    return "web_search", task


def run_agent(task, model=MODEL, tools=TOOLS):
    tool_name, tool_input = route(task)
    tool_output = tools[tool_name](tool_input)
    answer = model([{"role": "user", "content": tool_output}])
    return {"tool": tool_name, "answer": answer}


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"tool={result['tool']}\nanswer={result['answer']}")
