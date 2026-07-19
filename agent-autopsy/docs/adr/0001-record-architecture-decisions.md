# 1. Record Architecture Decisions

Date: 2026-05-07

## Status

Accepted

## Context

Per classHuman AI Engineering Standards, all classHuman AI repositories maintain Architecture Decision Records to capture significant technical and design choices. ADRs preserve the *why* behind decisions, which would otherwise be lost to commit history and future memory — a particular concern given TBI-driven need to keep context externalized rather than carried in working memory.

## Decision

We will record significant architectural decisions for `agent-autopsy` in this directory, following the lightweight ADR format pioneered by Michael Nygard.

Each ADR has:
- A title in the form `NNNN-short-title.md`
- Numbered sequentially
- Sections: Status, Context, Decision, Consequences

Significant decisions include (non-exhaustive):
- Choice of model provider or SDK
- Repo structure changes
- Test strategy changes
- License or distribution changes
- Course-to-code mapping decisions

## Consequences

- Decisions become inspectable artifacts, not folklore
- New contributors (or future-Lawrence) can read the repo history without losing the design intent
- Adds a small overhead per significant decision; trivial decisions still go in commits, not ADRs

## References

- classHuman AI `VERSIONING.md` and `DOCUMENTATION.md` standards
- [Michael Nygard's ADR pattern](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

---

*LAHA — Love All Humans Always.*
