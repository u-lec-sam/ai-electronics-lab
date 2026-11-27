# Architecture

## Roles
- **ChatGPT:** requirements analysis, design proposals, schematic/PCB source authoring, firmware authoring, review, and supported GitHub file updates.
- **GitHub:** source of truth, persistent project memory, decision history, experiment archive, and version history.
- **GitHub Actions:** repeatable, deterministic validation and build automation.
- **KiCad:** native schematic and PCB engineering environment.
- **KiCanvas:** optional browser viewing; it does not replace full KiCad editing or electrical verification.

## Session-start read protocol
For every substantive AI Electronics Lab work session, ChatGPT must read the current GitHub state before proposing or changing project files:
1. Confirm repository identity, default branch, and latest commit.
2. Read `README.md`, this file, `docs/ENGINEERING_RULES.md`, and `docs/RECURSIVE_IMPROVEMENT.md`.
3. Read the active project's README, design brief, interface plan, BOM, and relevant source files.
4. Inspect recent commits and the latest applicable CI status when the connector exposes them.
5. Summarize the current verified state, open questions, failed checks, and next safe action.
6. Never assume a previous chat summary is newer than GitHub. GitHub is the project source of truth.

If GitHub cannot be read, explicitly say that repository state was not refreshed and do not claim to have checked it.

## Workflow
1. Define requirements and constraints.
2. Select exact parts and verify manufacturer documentation.
3. Create schematic and review symbol pins/net connectivity.
4. Run ERC, then create PCB and run DRC.
5. Build firmware with a pinned, licensed toolchain.
6. Review power, thermal, signal integrity, clearances, and manufacturing constraints.
7. Release Gerbers, drill files, BOM, assembly outputs, and firmware only after review.

## Automation boundary
GitHub Actions can run deterministic scripts and toolchains on repository events. It does not independently perform engineering judgment. ChatGPT can act when prompted in the conversation; this is not an always-on autonomous agent and does not modify its underlying model weights through repository commits.

## MCU profiles
Keep platform-specific startup code, linker scripts, SDK/HAL acquisition, compiler versions, and CI commands isolated under `platforms/` or each project's `firmware/`.
