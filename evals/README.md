# Evaluation Suite

This directory tests the agent scaffold and repository contracts, not the intelligence of the hosted foundation model.

## Evaluation layers

1. **Repository contract:** required project memory, architecture, and safety boundaries remain present.
2. **Artifact validation:** CSV structure, source syntax, and project completeness checks.
3. **Task benchmarks:** later add fixed, versioned engineering tasks with expected outputs and scoring rubrics.
4. **Regression set:** every meaningful failure becomes a reproducible test when feasible.
5. **Independent review:** important hardware claims require datasheet evidence, simulation, independent review, or measurements as appropriate.

## Rules against evaluator gaming

- Do not delete or weaken a failing test merely to improve a score.
- Changes to test expectations require a separate rationale and review.
- Keep old regression cases when adding new ones.
- Report skipped tests distinctly from passed tests.
- A passing software test does not establish circuit safety, manufacturability, or physical correctness.

## Running locally or in CI

```bash
python scripts/validate_project.py
python -m unittest discover -s evals -p 'test_*.py' -v
gcc -std=c11 -Wall -Wextra -Werror -fsyntax-only projects/001-stm32g0b1-sensor-io/firmware/src/main.c
```
