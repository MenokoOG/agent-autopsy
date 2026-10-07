---
title: "Failure 11: The confident liar"
permalink: /failures/11-confident-liar/
---

# Failure 11: The confident liar

*Search returned nothing. The agent reported "$4.21 billion, up 12%" with a citation it invented.*

## The scenario

You ask the agent for a company's third-quarter revenue. The company is private, the number isn't public, and the search tool comes back empty. But the model was asked for a number, and a language model asked for a number tends to produce one. It writes a specific, plausible, wrong figure, often with a source attached that doesn't exist.

The user can't tell grounded from invented. That's the worst part of this failure: the lie looks exactly like the truth.

The code is in [`11-confident-liar`](https://github.com/MenokoOG/agent-autopsy/tree/main/agent-autopsy/11-confident-liar).

## The bug

From [`broken.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/11-confident-liar/broken.py):

```python
def search(query):
    return []  # no results. ACME is private; the number isn't out there.

def run_agent(task, model=MODEL, search_tool=search):
    evidence = search_tool(task)

    # THE BUG: the answer never has to point at evidence. Empty search
    # results and a confident reply coexist just fine — and ship.
    prompt = f"{task}\n\nSearch results: {evidence}"
    return {"answer": model(prompt), "evidence": evidence}
```

The agent has an empty list and asks the model anyway. Output:

```text
evidence: []
answer:   ACME Corp reported Q3 2025 revenue of $4.21 billion, up 12% year-over-year (source: ACME investor relations).
```

The result object contains both facts: `evidence: []` and a detailed answer. They contradict each other, and nothing in the code compares them. The prompt says "Search results: []", which a careful reader reads as "you have no information." The model reads it as a formatting detail and keeps going.

## Why it happens

A model optimizes for a fluent, helpful-looking reply. "I don't know" is a less likely continuation than a number, because most text in training that follows a question like this contains an answer. The model also can't see the difference between recalling a fact and generating one that fits the pattern.

You can ask nicely in the prompt: "only answer from the search results." That helps, and it fails some of the time. A rule that fails some of the time isn't a safeguard.

## The fix

[`fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/11-confident-liar/fixed.py) enforces grounding in code, with two gates.

**Gate 1: no evidence, no factual answer.**

```python
if not evidence:
    return {"answer": NO_DATA_ANSWER, "evidence": [], "grounded": False}
```

When the search comes back empty, the function never calls the model. The honest answer is computed, not generated. There's nothing for the model to make up, because it isn't asked.

**Gate 2: reject specific claims that carry no citation.**

```python
numbered = "\n".join(f"[{i}] {e}" for i, e in enumerate(evidence))
prompt = (f"{task}\n\nEvidence:\n{numbered}\n\n"
          "Answer using ONLY the evidence above. Cite [n] for every claim. "
          "If the evidence doesn't contain the answer, say so.")
answer = model(prompt)

if contains_specific_claims(answer) and not re.search(r"\[\d+\]", answer):
    return {"answer": NO_DATA_ANSWER, "evidence": evidence, "grounded": False}

return {"answer": answer, "evidence": evidence, "grounded": True}
```

When there is evidence, the prompt numbers it and asks for `[n]` citations. After the model replies, the code checks the reply. If it contains numbers, dollar amounts or percentages and has no citation, it's rejected.

Run it:

```text
grounded: False
answer:   I could not verify this. My search returned no results for ACME Corp Q3 2025 revenue, so I won't state a figure.
```

The result carries a `grounded` flag, so the caller can tell a verified answer from a refusal without parsing prose.

## The proof

The tests in [`tests/test_fixed.py`](https://github.com/MenokoOG/agent-autopsy/blob/main/agent-autopsy/11-confident-liar/tests/test_fixed.py):

- `test_fixed_refuses_without_evidence` checks gate 1.
- `test_fixed_rejects_uncited_specifics_even_with_evidence` checks gate 2 catches a model that has evidence and still ignores it.
- `test_fixed_accepts_cited_grounded_answer` checks a good answer passes.
- `test_broken_ships_the_fabrication` pins the original lie.

## Where the fix stops

This is the lesson where the gap between the demo and production is widest, so read this section twice.

- **Gate 2 checks that a citation exists, not that it's right.** The test is `re.search(r"\[\d+\]", answer)`. An answer that says "$9 trillion [7]" when there's one piece of evidence passes. A model can attach a citation to an invented claim. Production checks verify that each cited index exists and that the claim appears in that evidence, by string match for numbers or with a second model acting as a verifier.
- **The claim detector is crude.** `contains_specific_claims` matches any digit. It will flag harmless replies like "see section 2" and could miss a claim made in words, like "four billion". Treat it as a tripwire to tune.
- **Gate 1 assumes empty means unknown.** An empty list can also mean the search tool failed. That's [failure 5]({{ '/failures/05-silent-tool-failure/' | relative_url }}) again: check the tool result before trusting it either way.
- **Irrelevant evidence passes gate 1.** If search returns three unrelated articles, `evidence` isn't empty and the model is free to answer from thin air. Check relevance, not only existence.
- **The refusal text is hard-coded to this question.** `NO_DATA_ANSWER` names ACME Corp and Q3 2025. Generate it from the query in real code.

## The takeaway

Grounding is enforced in code and never requested in the prompt. No evidence means no factual answer, decided by an `if` statement instead of the model's conscience, and claims without citations get rejected on the way out.

---

[&larr; Previous: Failure 10]({{ '/failures/10-prompt-injection/' | relative_url }}) · [Next: Failure 12, no human brake &rarr;]({{ '/failures/12-no-human-brake/' | relative_url }}) · [All failures]({{ '/' | relative_url }})
