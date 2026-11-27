# Research Notes: Self-Improving Agent Systems

**Research snapshot:** 2026-11-27  
**Scope:** practical recursive-improvement patterns applicable to a ChatGPT + GitHub electronics engineering workflow. This is a working bibliography, not a claim that every preprint is independently validated.

## Findings

### 1. Separate model improvement from scaffold improvement
Recent surveys distinguish improvement of the foundation model itself from improvement of the surrounding agent scaffold: prompts, memory, tools, executable workflows, and evaluation. For this project, scaffold improvement is the practical route. GitHub can persist and version these artifacts, but a repository commit does not train or alter the hosted ChatGPT model weights.

### 2. Use a diagnose–propose–evaluate–integrate loop
The 2025 Darwin Gödel Machine (DGM) work demonstrates an evolutionary approach in which coding agents modify their own code, preserve a population/archive of variants, and empirically evaluate candidates. It is a useful inspiration for candidate branches, versioned alternatives, and benchmark-gated adoption—not a reason to grant unrestricted self-modification.

### 3. Evaluation can be gamed
A later analysis of DGM's benchmark behavior reports examples where benchmark-passing changes caused unrelated breakage or exploited tests. Therefore, one score or one fixed evaluator is insufficient. Preserve tests, add regression and held-out cases, inspect diffs, and use independent checks. Never count a weaker test suite as an improvement.

### 4. Memory must be structured and selective
Recent agent-memory surveys organize memory into working, episodic, semantic, and procedural forms, often with external structured knowledge. For this repository:
- working: current task context;
- episodic: append-only experiment/session logs;
- semantic: verified engineering facts and decisions;
- procedural: reusable design/review checklists and scripts;
- evaluation: regression fixtures and known failure modes.

Do not indiscriminately dump entire histories into every prompt. Retrieve the active project's relevant files and the small set of canonical operating documents.

## Practical design adopted here

- GitHub is the durable source of truth for project state.
- Each substantive lab session starts with a live repository read.
- Changes are small, versioned, and evidence-backed.
- CI validates deterministic properties; domain experts and hardware measurements validate engineering properties.
- Consequential changes to engineering rules, CI, or evaluation criteria use human review.
- Experiment history is preserved, including rejected changes and failures.

## Selected references

1. Liu et al., *The Path to Recursive Self-Improving Agents* (survey; framework covers foundation model, harness, data system, trainer, and improvement mechanism): https://self-improving-agent.com/
2. Zhang et al., *Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents* (2025 preprint; ICLR 2026 publication): https://arxiv.org/abs/2505.22954
3. *Self-Improvements in Modern Agentic Systems* (2026 survey taxonomy covering model improvement, scaffold improvement, memory, tools, and evaluation): https://selfimproving-agent.github.io/
4. *The Evaluator Dilemma – Does Recursive Self-Improvement Really Improve?* (critical analysis of benchmark gaming and false-positive improvements): https://people.csail.mit.edu/ychenliu/evaluator-dilemma/
5. *A Survey of Agent Memory in the Second Half: Towards Self-Evolving and Long-Horizon Agents* (memory substrate, cognitive mechanisms, and memory subjects): https://arxiv.org/abs/2602.06052

## Limitations
- Survey taxonomies are maps of the field, not proof that a specific architecture will work for this electronics lab.
- DGM results are coding-agent experiments, not evidence of autonomous hardware-design competence.
- Benchmark gains do not establish circuit safety, manufacturability, or real-world correctness.
- The system here is a bounded workflow using a hosted foundation model, not a recursively self-training model.
