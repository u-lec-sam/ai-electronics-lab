# Decision 0001: Improve the Agent Scaffold, Not Hosted Model Weights

- **Date:** 2026-11-27
- **Status:** accepted
- **Scope:** AI Electronics Lab operating architecture

## Context

The project wants a practical recursive-improvement workflow using ChatGPT and GitHub. The hosted model's internal weights are not writable through repository operations, and commits do not train the model.

## Decision

Treat the versioned agent scaffold as the improvement surface:

- repository retrieval and memory organization;
- prompts, procedures, templates, and engineering checklists;
- deterministic scripts, CI workflows, and tool integrations;
- evaluation cases, regression tests, and experiment selection;
- project artifacts such as schematics, PCB sources, and firmware.

Use measured candidate comparisons. Preserve a known-good baseline and keep experiments traceable. For core workflow or evaluation changes, use a feature branch and pull request.

## Non-goals

- Claiming that GitHub commits change ChatGPT model weights.
- Unrestricted autonomous rewriting of safety rules or evaluators.
- Treating benchmark or CI success as proof of physical hardware correctness.

## Consequences

The system can improve its repeatability, retrieval, tool use, engineering artifacts, and validation coverage over time. Actual foundation-model training or fine-tuning would require a separate supported training workflow, data governance, compute, and evaluation program.
