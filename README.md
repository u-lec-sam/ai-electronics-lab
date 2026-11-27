# AI Electronics Lab

AI-first, GitHub-centered electronics design workspace. MCP is not required for this workflow.

## Supported platforms
- STMicroelectronics: STM32
- Texas Instruments: MSPM0, C2000, MSP430
- Espressif: ESP32
- Other MCU families through additional platform profiles

## Repository principles
1. GitHub is the source of truth for design files, firmware, documentation, and releases.
2. ChatGPT assists with requirements, design, source generation, review, and supported repository updates.
3. GitHub Actions performs repeatable automated checks.
4. KiCad native files are the editable hardware source. KiCanvas may be used as a browser viewer.
5. No design is fabrication-ready until electrical, layout, thermal, and manufacturing checks pass.

## First project
See [AEL-001: STM32G0B1 Sensor & I/O Controller](projects/001-stm32g0b1-sensor-io/README.md).

**Current status: preliminary design brief only.** No completed schematic, PCB, ERC/DRC result, or flashable firmware is claimed yet.

## Layout
- `docs/`: architecture and engineering rules
- `projects/`: project-specific hardware, firmware, BOM, and validation
- `platforms/`: MCU family toolchain profiles
- `.github/workflows/`: automated CI
- `scripts/`: validation utilities

## Public repository warning
All committed files and history are public. Never commit credentials, private data, or proprietary material without redistribution permission.
