# Project Memory

This directory is the durable, curated memory layer for AI Electronics Lab. GitHub is the source of truth; ChatGPT's conversational memory is supplementary and may be incomplete.

## Memory classes

- `PROJECT_STATE.md`: compact current-state snapshot. Update when verified project state materially changes.
- `episodes/`: append-only session and experiment summaries. Preserve failures and rejected hypotheses.
- `knowledge/`: curated, evidence-backed technical knowledge. Every nontrivial claim should link to a source, revision, or test.
- `decisions/`: append-only architectural and engineering decisions. Supersede decisions explicitly; do not erase history.

## Retrieval policy

At the start of every substantive task:
1. Read the repository's current default branch and latest commit.
2. Read `README.md`, `docs/ARCHITECTURE.md`, `docs/ENGINEERING_RULES.md`, and `docs/RECURSIVE_IMPROVEMENT.md`.
3. Read this index and `PROJECT_STATE.md`.
4. Retrieve only the active project's relevant files and related episodes/decisions/evaluations.
5. Prefer current source files and evidence over summaries.

Do not copy the entire repository history into every prompt. Retrieve the smallest relevant evidence set and preserve links to original files/commits.

## Integrity rules

- Never present an assumption as verified fact.
- Never silently rewrite historical episodes or decisions.
- Correct errors by adding a dated correction or superseding decision.
- Never store credentials, tokens, private personal data, or secrets.
- A memory item is useful only if it improves retrieval or decisions; avoid duplicate or speculative notes.
