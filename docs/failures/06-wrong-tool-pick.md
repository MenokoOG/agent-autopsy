---
title: "Failure 6: Wrong tool pick"
permalink: /failures/06-wrong-tool-pick/
---

# Failure 6: Wrong tool pick

*The question was arithmetic. The agent searched the web and returned a 2019 forum guess.*

## The scenario

A user asks, "What is 12.5% of 3,847?" Your router sees a question that starts with "What is", classifies it as a lookup, and sends it to web search, the tool it reaches for on everything. Search returns a stale snippet that sounds sure of itself. The agent passes it along. The calculator, which would have nailed the answer in microseconds, never runs.

The code is in [`06-wrong-tool-pick`](https://github.com/MenokoOG/agent-autopsy/tree/main/06-wrong-tool-pick).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/06-wrong-tool-pick/broken.py):

```python
def route(task):
    # THE BUG: routing by vibes. "What is..." looks like a lookup question,
    # so everything routes to search. No one asked what the task NEEDS.
    return "web_search"


def run_agent(task, model=MODEL, tools=TOOLS):
    tool_name = route(task)
    tool_output = tools[tool_name](task)
    answer = model([{"role": "user", "content": tool_output}])
    return {"tool": tool_name, "answer": answer}
```

The router in this demo is one line, and that's deliberate. Many real routers are only a little more elaborate: a keyword list, a similarity score, a prompt that says "pick the best tool." They share the flaw. They decide from how the question looks.

The output:

```text
tool=web_search
answer=Top result (forum, 2019): '12.5% of 3,847 is about 480.'

correct answer: 480.875
```

Look at the answer itself. "About 480" is wrong by 0.875, and it came with a source, a date and a confident tone. Nothing marks it as wrong. This is a sibling of [failure 5]({{ '/failures/05-silent-tool-failure/' | relative_url }}): the system produced a plausible answer, and nothing in the output signals that the wrong tool ran.

## Why it happens

Search is a good default for "what is" questions about the world. It's a bad default for questions whose answer is fully determined by the input. Arithmetic, date math, unit conversion and string formatting don't live on the internet. They live in code. A model asked to compute these by itself is unreliable. A search engine is worse, since it returns whatever some page once said.

Routers drift toward the tool with the broadest coverage. Broad tools win ties, and ties are common.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/06-wrong-tool-pick/fixed.py) routes on what the task needs and tries a deterministic classifier first:

```python
def extract_math(task):
    """Turn 'What is 12.5% of 3,847?' into a computable expression."""
    m = re.search(r"([\d.,]+)\s*%\s*of\s*([\d.,]+)", task)
    if m:
        pct, base = (float(g.replace(",", "")) for g in m.groups())
        return f"{pct} / 100 * {base}"
    m = re.search(r"[\d.,]+(\s*[-+*/]\s*[\d.,]+)+", task)
    return m.group(0).replace(",", "") if m else None


def route(task):
    expression = extract_math(task)
    if expression:
        return "calculator", expression
    return "web_search", task
```

Two changes matter.

**The router returns the tool and its input.** The broken router sent the raw question text to whatever tool it picked. The new one transforms the question into something the tool can use: `12.5 / 100 * 3847.0` for the calculator. Routing and argument preparation belong together, because a tool is only the right choice if you can call it correctly.

**Rules come first, search is the fallback.** If the task matches a pattern for exact computation, the calculator gets it. Otherwise the default still applies. The default changed from "always search" to "search when nothing more specific fits."

Run it:

```text
tool=calculator
answer=480.875
```

The proof of the right result is the number: 480.875, which matches the broken script's own "correct answer" line.

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/06-wrong-tool-pick/tests/test_fixed.py):

- `test_fixed_routes_math_to_calculator` checks the percentage question reaches the calculator.
- `test_fixed_routes_plain_arithmetic` checks a plain expression does too.
- `test_fixed_still_searches_for_facts` guards the other side: a real lookup still goes to search. A router that over-corrects into the calculator is just as broken.
- `test_broken_searches_for_math_and_gets_it_wrong` pins the original behavior.

## Where the fix stops

- **Regexes cover the cases you thought of.** "A 12.5 percent share of 3,847" doesn't match. "Twelve and a half percent of 3847" doesn't either. A rules-first router is a floor, and its coverage grows only as you add patterns and test them.
- **Model-based routing is still needed for ambiguous tasks.** The repo's note says it directly: deterministic first, model fallback second. When you do let a model choose, give it a description of what each tool is for and when not to use it, and check the choice against the task type.
- **The tool's output still needs checking.** Picking the right tool doesn't remove the need for the boundary check from failure 5.
- **The calculator uses `eval`.** It runs with empty builtins in this demo, which is not a safe sandbox for untrusted input. Replace it with a real expression parser before you reuse the idea.

## The takeaway

Route on what the task needs, not on what the question looks like. Exact computation goes to a calculator, and fresh external facts go to search. A small deterministic classifier for the easy cases beats a vibes-based default every time.

---

[&larr; Previous: Failure 5]({{ '/failures/05-silent-tool-failure/' | relative_url }}) · [Next: Failure 7, context collapse &rarr;]({{ '/failures/07-context-collapse/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
