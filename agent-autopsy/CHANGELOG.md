# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Every PR includes its CHANGELOG entry in the diff.

## [Unreleased]

### Added
- Written lesson series for all 12 failures, published with GitHub Pages from `docs/`

### Changed
- Removed brand references from the README, folder READMEs and LICENSE
- Folder READMEs link to the matching article on the Pages site

## [0.2.0] - 2026-07-19

### Added
- Runnable `broken.py` and `fixed.py` for all 12 failures (mock model by default — no API key or token spend needed; real Anthropic SDK used automatically when `ANTHROPIC_API_KEY` is set)
- `tests/test_fixed.py` for all 12 failures: 53 pytest cases proving each fix holds and each broken version fails the way prod fails
- Folder READMEs for failures #2–#12 following the `docs/STRUCTURE.md` template
- `pytest.ini` (importlib import mode) so the whole suite runs from the repo root

### Changed
- Branding references updated (LAHA)
- Course platform: Udemy references replaced with a written lesson series
- LICENSE copyright holder updated to Lawrence Jefferson II

## [0.1.0] - 2026-05-07

### Added
- Initial repository skeleton
- README with the 12-failure index
- Folder structure for all 12 failures, each with `tests/`
- Failure #1 README as the working template
- `docs/STRUCTURE.md` describing the per-folder pattern
- `docs/adr/0001-record-architecture-decisions.md` 
- `VERSIONING.md` and `DOCUMENTATION.md` placeholders
- LICENSE (MIT), `.env.example`, `.gitignore`, `requirements.txt`, `VERSION`
