"""Failure #4: Tool Hallucination (FIXED).

Every tool request is validated against the registry. Unknown tool? The
agent tells the model what actually exists and lets it retry, bounded at
three attempts, logged, and failing loud instead of crashing blind.

Run: python fixed.py   (mock model unless ANTHROPIC_API_KEY is set)
"""
import ast
import json
import operator
import os

TASK = "How many active users do we have?"
MAX_TOOL_RETRIES = 3


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
    # First ask: hallucinate. After being corrected: pick a real tool.
    corrected = any("Unknown tool" in m["content"] for m in messages)
    if corrected:
        return json.dumps({"tool": "web_search", "args": {"query": "active user count"}})
    return json.dumps({"tool": "database_query",
                       "args": {"sql": "SELECT COUNT(*) FROM users WHERE active=1"}})


MODEL = real_model if os.environ.get("ANTHROPIC_API_KEY") else mock_model


def run_agent(task, model=MODEL, tools=TOOLS, max_retries=MAX_TOOL_RETRIES):
    messages = [{"role": "user", "content": task}]
    attempts = []

    for attempt in range(1, max_retries + 1):
        request = json.loads(model(messages, tools))
        name = request.get("tool")
        attempts.append(name)

        # THE FIX: validate before executing. The registry is the source of
        # truth, the model's imagination is not.
        if name not in tools:
            messages.append({"role": "assistant", "content": json.dumps(request)})
            messages.append({"role": "user", "content":
                             f"Unknown tool {name!r}. Available tools: "
                             f"{sorted(tools)}. Pick one of those."})
            continue

        result = tools[name](**request["args"])
        return {"tool": name, "result": result, "attempts": attempts}

    raise RuntimeError(f"No valid tool chosen after {max_retries} attempts: {attempts}")


if __name__ == "__main__":
    outcome = run_agent(TASK)
    print(f"attempts={outcome['attempts']}")
    print(f"used {outcome['tool']!r} -> {outcome['result']}")
