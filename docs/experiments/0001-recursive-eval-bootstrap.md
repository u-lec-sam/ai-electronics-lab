# Experiment 0001: Recursive Evaluation Bootstrap

- **Date:** 2026-11-27
- **Candidate branch:** `agent/recursive-evaluation-bootstrap`
- **Baseline commit:** `ccdf16b1fbb3c1b594440d9f7ccc63e05c53b89e`
- **Status:** pending CI evidence

## Problem and evidence

The baseline had a written recursive-improvement protocol and a basic repository validator, but no dedicated evaluation suite for critical operating contracts. The KiCad CI job also installed KiCad on every run even when no native KiCad files existed.

## Baseline

- Repository validation checked a limited set of files and CSV row presence.
- No dedicated tests guarded the recursive-improvement protocol, memory policy, or project status boundaries.
- The latest inspected workflow run for the baseline commit completed successfully; no KiCad source files were present, so this was not an ERC/DRC pass.

## Hypothesis

A small standard-library test suite plus conditional KiCad CI will improve detection of repository drift and avoid unnecessary KiCad installation when no schematic/PCB exists.

## Candidate changes

- Add structured memory, decisions, experiments, and evaluation documentation.
- Add repository-contract tests using Python's standard library.
- Run those tests in CI.
- Run the KiCad job only when native KiCad files are present.
- Add bounded job timeouts and explicit read-only CI permissions.

## Acceptance criteria

1. All repository-contract tests pass.
2. Existing scaffold validation and C syntax checks remain enabled.
3. KiCad is not represented as verified when no native files exist.
4. No engineering safety rule or test is removed to obtain a green result.
5. Candidate diff is reviewed before integration.

## Results

- The first workflow revision failed before creating any jobs because the job-level conditional was invalid for the chosen expression context.
- The KiCad guard was moved to individual steps. This preserved the desired behavior without skipping the whole job.
- GitHub Actions run 19 for candidate commit `558fcbaa3fbb7c5c8dd0ed7a4a8f57084861ab49` completed successfully.
- Scaffold validation: passed.
- Repository-contract tests: passed.
- C scaffold syntax check: passed.
- KiCad installation/ERC/DRC: skipped because no native KiCad schematic or PCB files exist. This is not an ERC/DRC pass.
- The initial failed workflow run remains part of the experiment history; it was not erased.

## Decision

Accepted for integration after review. The candidate meets the stated software/repository acceptance criteria. Hardware correctness is outside this experiment.
