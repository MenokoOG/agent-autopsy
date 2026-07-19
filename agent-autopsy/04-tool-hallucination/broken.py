"""Failure #4 — Tool Hallucination (BROKEN).

The model asks for a tool that doesn't exist — `database_query`, invented
from thin air because it sounds plausible. The agent code trusts the request
blindly and crashes with a KeyError at 2 a.m.

Run: python broken.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import json
import os

TASK = "How many active users do we have?"


def calculator(expression):
    return str(eval(expression, {"__builtins__": {}}, {}))


def web_search(query):
    return f"Search results for {query!r}: [3 articles about user growth]"


TOOLS = {"calculator": calculator, "web_search": web_search}


def real_model(messages, tools):
    from anthropic import Anthropic
    resp = Anthropic().messages.create(
        model="claude-sonnet-4-5", max_tokens=300, messages=messages
    )
    return resp.content[0].text


def mock_model(messages, tools):
    # The model invents a plausible-sounding tool nobody registered.
    return json.dumps({"tool": "database_query",
                       "args": {"sql": "SELECT COUNT(*) FROM users WHERE active=1"}})


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL):
    messages = [{"role": "user", "content": task}]
    request = json.loads(model(messages, TOOLS))

    # THE BUG: whatever tool name the model emits gets executed. No check
    # that it exists, no correction loop. KeyError in prod, stack trace, page.
    tool_fn = TOOLS[request["tool"]]
    result = tool_fn(**request["args"])
    return {"tool": request["tool"], "result": result}


if __name__ == "__main__":
    print(run_agent(TASK))
