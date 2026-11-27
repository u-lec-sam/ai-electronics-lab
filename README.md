# AI Electronics Lab

AI-first, GitHub-centered electronics design and iterative-improvement workspace. MCP is not required for the current workflow.

## Operating principle
At the start of every substantive lab session, ChatGPT refreshes and reads the current GitHub repository before planning or editing. The repository is the durable project memory and source of truth. Improvements follow the documented READ → BASELINE → DIAGNOSE → PROPOSE → TEST → REVIEW → INTEGRATE → RECORD loop.

See [Recursive Improvement Protocol](docs/RECURSIVE_IMPROVEMENT.md) and [Research Notes](docs/RESEARCH_NOTES.md).

## Supported platforms
- STMicroelectronics: STM32
- Texas Instruments: MSPM0, C2000, MSP430
- Espressif: ESP32
- Other MCU families through additional platform profiles

## First project
See [AEL-001: STM32G0B1 Sensor & I/O Controller](projects/001-stm32g0b1-sensor-io/README.md).

**Current status: preliminary design brief only.** No completed schematic, PCB, ERC/DRC result, or flashable firmware is claimed yet.

## Layout
- `docs/`: architecture, engineering rules, improvement protocol, research notes, experiments
- `projects/`: project-specific hardware, firmware, BOM, and validation
- `platforms/`: MCU family toolchain profiles
- `.github/workflows/`: automated CI
- `scripts/`: validation utilities

## Public repository warning
All committed files and history are public. Never commit credentials, private data, or proprietary material without redistribution permission.
