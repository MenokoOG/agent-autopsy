# Failure Folder Structure

Every folder follows the same pattern. This keeps the repo predictable for students and easy to extend.

## Required files

```
NN-failure-name/
├── README.md         # what, why, fix-in-one-sentence
├── broken.py         # the bug, runnable, fails the way prod fails
├── fixed.py          # the fix, minimal diff from broken.py
└── tests/
    └── test_fixed.py # proves the fix holds
```

## README template

Each folder README has these sections, in order:

1. **Title** — `# Failure #N — The [Name]`
2. **Quote** — one-line gut-punch description
3. **What it looks like in production** — 2–4 sentences, concrete scenario
4. **The lesson** — bold one-liner, then 1–2 sentences expanding it
5. **Files in this folder** — bullet list
6. **Try it yourself** — copy-paste commands
7. **The fix in one sentence** — the takeaway
8. **Watch the lesson** — link to the course

## Code style

- Both `broken.py` and `fixed.py` should be **runnable standalone** with just `ANTHROPIC_API_KEY` set.
- Keep each file under 100 lines where possible. The lesson should be readable in one sitting.
- The diff between broken and fixed should be small and obvious. The smaller the diff, the harder the lesson hits.
- Add comments only where the lesson lives. Don't over-comment trivial code.
- Use the Anthropic SDK by default (model: `claude-sonnet-4-5` or current). Mention OpenAI alternative in the README if relevant.

## Test style

- One test per failure mode the fix prevents.
- Tests should fail against `broken.py` and pass against `fixed.py`.
- Mock the model call where possible — students shouldn't need to spend money to run tests.
