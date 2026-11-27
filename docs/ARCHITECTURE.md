# Architecture

## Roles
- **ChatGPT:** requirements analysis, design proposals, schematic/PCB source authoring, firmware authoring, review, and supported GitHub file updates.
- **GitHub:** source of truth and version history.
- **GitHub Actions:** reproducible validation and build automation.
- **KiCad:** native schematic and PCB engineering environment.
- **KiCanvas:** optional browser viewing; it does not replace full KiCad editing or electrical verification.

## Workflow
1. Define requirements and constraints.
2. Select exact parts and verify manufacturer documentation.
3. Create schematic and review symbol pins/net connectivity.
4. Run ERC, then create PCB and run DRC.
5. Build firmware with a pinned, licensed toolchain.
6. Review power, thermal, signal integrity, clearances, and manufacturing constraints.
7. Release Gerbers, drill files, BOM, assembly outputs, and firmware only after review.

## Automation boundary
GitHub Actions can run deterministic scripts and toolchains on repository events. It does not independently perform engineering judgment. ChatGPT can act when prompted in the conversation; this is not an always-on autonomous agent.

## MCU profiles
Keep platform-specific startup code, linker scripts, SDK/HAL acquisition, compiler versions, and CI commands isolated under `platforms/` or each project's `firmware/`.
