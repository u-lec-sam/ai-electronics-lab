# AI Electronics Lab

AI-first, GitHub-centered electronics design and iterative-improvement workspace. MCP is not required for the current workflow.

## Operating principle

At the start of every substantive lab session, ChatGPT refreshes and reads the current GitHub repository before planning or editing. The repository is the durable project memory and source of truth. Improvements follow the documented recursive-improvement loop.

The improvement target includes both engineering artifacts and the agent scaffold that produces them: retrieval, memory, procedures, tools, CI, and evaluation. This does not modify the hosted ChatGPT model weights.

**Low-effort operation:** ChatGPT chooses and performs the next safe task, maintains one prioritized next action, and ends substantive progress reports with one **Run next task** button. The button resumes work only when pressed; it is not a background daemon. See [One-Button Operator Loop](docs/ONE_BUTTON_OPERATOR_LOOP.md).

See:
- [Architecture](docs/ARCHITECTURE.md)
- [Recursive Improvement Protocol](docs/RECURSIVE_IMPROVEMENT.md)
- [Research Notes](docs/RESEARCH_NOTES.md)
- [Project Memory](memory/README.md)
- [Evaluation Suite](evals/README.md)

## Supported platforms
- STMicroelectronics: STM32
- Texas Instruments: MSPM0, C2000, MSP430
- Espressif: ESP32
- Other MCU families through additional platform profiles

## First project
See [AEL-001: STM32G0B1 Sensor & I/O Controller](projects/001-stm32g0b1-sensor-io/README.md).

**Current status: preliminary design brief only.** No completed schematic, PCB, ERC/DRC result, or flashable firmware is claimed yet.

## Layout
- `docs/`: architecture, engineering rules, improvement protocol, research, decisions, experiments
- `memory/`: curated project state and durable memory index
- `evals/`: repository contracts and future agent/task benchmarks
- `projects/`: project-specific hardware, firmware, BOM, and validation
- `platforms/`: MCU family toolchain profiles
- `.github/workflows/`: automated CI
- `scripts/`: validation utilities

## User interaction and safety boundary

Minimize user effort. The agent should perform repository research, file editing, tests, and evidence recording when supported. Ask the user only for decisions or physical actions that cannot be safely or truthfully completed by the agent. Never access the user's local device or imply local access. Consequential hardware, safety, cost, credential, and public-disclosure actions remain gated.

## Public repository warning

All committed files and history are public. Never commit credentials, private data, or proprietary material without redistribution permission.
