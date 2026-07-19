# Versioning

> **This file is a placeholder.** Replace with the canonical [`VERSIONING.md`](https://claude.ai/local_sessions/local_53f6fedf-1a43-46e2-890b-5dece115bf5c) from `~/development/claude-mds/standards/` before publishing.

## Summary of the standard this repo follows

This project follows the classHuman AI Engineering Standards versioning policy:

- **Three-tier semver** in `VERSION` (currently `0.1.0`)
- **`CHANGELOG.md`** in [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format
- **CHANGELOG entry required in every PR diff** — a PR is not mergeable until its changelog entry is part of the diff
- **Bump rules** follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):
  - `MAJOR` — breaking changes to lesson contracts, repo structure, or public API
  - `MINOR` — new failures, new lessons, new test infrastructure (backwards-compatible)
  - `PATCH` — bug fixes, doc fixes, dependency bumps

## Current version

See [`VERSION`](./VERSION) and [`CHANGELOG.md`](./CHANGELOG.md).

---

*LAHA — Love All Humans Always. Versioning is how we keep faith with future-us.*
