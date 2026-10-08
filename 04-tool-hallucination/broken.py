"""Failure #4: Tool Hallucination (BROKEN).

The model asks for a tool that doesn't exist, `database_query`, invented
from thin air because it sounds plausible. The agent code trusts the request
blindly and crashes with a KeyError at 2 a.m.

Run: python broken.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import ast
import json
import operator
import os

TASK = "How many active users do we have?"


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}
_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}
MAX_EXPRESSION_CHARS = 200


def _evaluate(node):
    """Walk a parsed expression. Only numbers and + - * / % are allowed."""
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_evaluate(node.operand))
    raise ValueError(f"unsupported expression element: {type(node).__name__}")


def calculator(expression):
    if len(expression) > MAX_EXPRESSION_CHARS:
        raise ValueError("expression too long")
    return str(_evaluate(ast.parse(expression, mode="eval")))


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
