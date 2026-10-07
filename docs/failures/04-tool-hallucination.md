---
title: "Failure 4: Tool hallucination"
permalink: /failures/04-tool-hallucination/
---

# Failure 4: Tool hallucination

*The model asked for `database_query`. You never built a `database_query`. KeyError at 2 a.m.*

## The scenario

Your agent has two tools: a calculator and a web search. The user asks, "How many active users do we have?" The model reasons about what an agent in this situation should have, and requests a tool that sounds right: `database_query`, with a tidy SQL string. No such tool exists. Your dispatch code looks it up, the lookup fails, and the process crashes with a stack trace.

The worse version is a router that fuzzy-matches names. It sees `database_query`, finds something close, and runs the wrong real tool with arguments meant for a different one.

The code is in [`04-tool-hallucination`](https://github.com/MenokoOG/agent-autopsy/tree/main/04-tool-hallucination).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/04-tool-hallucination/broken.py):

```python
TOOLS = {"calculator": calculator, "web_search": web_search}

...

def run_agent(task, model=MODEL):
    messages = [{"role": "user", "content": task}]
    request = json.loads(model(messages, TOOLS))

    tool_fn = TOOLS[request["tool"]]
    result = tool_fn(**request["args"])
    return {"tool": request["tool"], "result": result}
```

The mock model returns `{"tool": "database_query", "args": {"sql": "SELECT COUNT(*) FROM users WHERE active=1"}}`. Run it:

```text
Traceback (most recent call last):
  ...
    tool_fn = TOOLS[request["tool"]]
KeyError: 'database_query'
```

Two assumptions are baked into that dictionary lookup. One: the model only names tools that exist. Two: the model's arguments match the tool's signature. Both hold in a demo and break in production. The model sees a list of tool names, but it also has a strong prior about what tools agents usually have. When the prior and the list disagree, the prior sometimes wins.

## Why it happens

Models predict plausible next tokens. A tool name is a token sequence like any other. If your prompt lists `calculator` and `web_search`, and the task smells like a database question, `database_query` is a very likely continuation. The model is completing a pattern, and a wrong tool name fits the pattern well.

Crashing is the good outcome. A crash is loud. The quiet outcomes are worse: a fuzzy matcher that picks the closest name, or a `try/except` that swallows the error and carries on without the result.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/04-tool-hallucination/fixed.py) validates every request against the registry and gives the model a chance to correct itself, with a limit:

```python
MAX_TOOL_RETRIES = 3

def run_agent(task, model=MODEL, tools=TOOLS, max_retries=MAX_TOOL_RETRIES):
    messages = [{"role": "user", "content": task}]
    attempts = []

    for attempt in range(1, max_retries + 1):
        request = json.loads(model(messages, tools))
        name = request.get("tool")
        attempts.append(name)

        if name not in tools:
            messages.append({"role": "assistant", "content": json.dumps(request)})
            messages.append({"role": "user", "content":
                             f"Unknown tool {name!r}. Available tools: "
                             f"{sorted(tools)}. Pick one of those."})
            continue

        result = tools[name](**request["args"])
        return {"tool": name, "result": result, "attempts": attempts}

    raise RuntimeError(f"No valid tool chosen after {max_retries} attempts: {attempts}")
```

The registry is the only source of truth. A request is a proposal until `name in tools` says otherwise. On a miss, the agent tells the model two things: what it asked for, and the sorted list of what exists. That's a correction the model can act on. The mock does:

```text
attempts=['database_query', 'web_search']
used 'web_search' -> Search results for 'active user count': [3 articles about user growth]
```

Three properties make this a good fix:

- **Bounded.** Three attempts, then a `RuntimeError`. This is the lesson from [failure 1]({{ '/failures/01-runaway-loop/' | relative_url }}) applied again: the retry loop has a cap.
- **Informative.** The error message names the registry. A correction that says only "wrong" teaches nothing.
- **Loud at the end.** If the model never recovers, the function raises and lists every attempted name: `['database_query', ...]`. You get a diagnosable failure instead of a silent one.

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/04-tool-hallucination/tests/test_fixed.py):

- `test_fixed_corrects_hallucinated_tool` checks the agent recovers after one correction.
- `test_fixed_fails_loud_when_model_never_recovers` uses a model that keeps inventing tools and checks the `RuntimeError` after the retry limit.
- `test_fixed_executes_valid_request_first_try` checks a good request runs with no extra calls.
- `test_broken_crashes_on_hallucinated_tool` pins the original `KeyError`.

## Where the fix stops

- **It validates the name and nothing else.** `tools[name](**request["args"])` still trusts the arguments. A real tool name with invented argument names raises a `TypeError` here. Validate arguments against a schema, such as JSON Schema or a typed model, before you call anything.
- **`request["args"]` can be missing.** The code uses `request.get("tool")` for the name but indexes `request["args"]` directly. A malformed request that has a valid tool name and no `args` key raises a `KeyError`. Treat the whole request as untrusted input.
- **`json.loads` can fail.** If the model returns prose instead of JSON, the parse raises before the validation runs. Production code catches that and feeds it back the same way.
- **Native tool calling helps.** If your API supports structured tool calls with declared schemas, the provider constrains the tool name for you. You still validate on your side. Don't rely on the provider as the only check.
- **The demo calculator uses `eval`.** Don't ship it. See the note on [the start page]({{ '/start-here/' | relative_url }}).

## The takeaway

The tool registry is the source of truth, and the model's imagination isn't. Validate every request before you execute it. On a miss, tell the model what exists and let it retry a few times, then fail loud.

---

[&larr; Previous: Failure 3]({{ '/failures/03-confidence-collapse/' | relative_url }}) · [Next: Failure 5, silent tool failure &rarr;]({{ '/failures/05-silent-tool-failure/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
