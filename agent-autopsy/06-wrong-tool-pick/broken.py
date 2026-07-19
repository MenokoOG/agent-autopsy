"""Failure #6 — Wrong Tool Pick (BROKEN).

The question is arithmetic. The agent reaches for web search — because
search is the hammer it always reaches for — and returns a stale forum
answer instead of doing the math.

Run: python broken.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import os

TASK = "What is 12.5% of 3,847?"


def calculator(expression):
    return str(eval(expression, {"__builtins__": {}}, {}))


def web_search(query):
    # The internet is full of confidently wrong, out-of-date snippets.
    return "Top result (forum, 2019): '12.5% of 3,847 is about 480.'"


TOOLS = {"calculator": calculator, "web_search": web_search}


def real_model(messages):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages):
    return messages[-1]["content"]  # echoes tool output as the final answer


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def route(task):
    # THE BUG: routing by vibes. "What is..." looks like a lookup question,
    # so everything routes to search. No one asked what the task NEEDS.
    return "web_search"


def run_agent(task, model=MODEL, tools=TOOLS):
    tool_name = route(task)
    tool_output = tools[tool_name](task)
    answer = model([{"role": "user", "content": tool_output}])
    return {"tool": tool_name, "answer": answer}


if __name__ == "__main__":
    result = run_agent(TASK)
    print(f"tool={result['tool']}\nanswer={result['answer']}")
    print(f"\ncorrect answer: {12.5 / 100 * 3847}")
