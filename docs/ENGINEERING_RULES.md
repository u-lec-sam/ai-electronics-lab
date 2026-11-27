# Engineering rules

1. Mark each design as concept, preliminary, verified, or released.
2. Do not invent pin numbers, package footprints, ratings, or alternate-function mappings.
3. Verify the exact orderable part, package, datasheet revision, reference manual, and errata.
4. Document the power tree, worst-case current, regulator dissipation, capacitor requirements, and protection strategy.
5. Check reset, boot, programming/debug access, decoupling, and unused pins.
6. Verify interface voltage levels, pull-ups, termination, ESD, and connector pinouts.
7. Run KiCad ERC and DRC on the actual committed native files before claiming a pass.
8. Do not claim firmware builds without the exact startup files, linker script, SDK/HAL, and compiler configuration.
9. Public repository contents and history are visible to everyone. Do not commit secrets or files without redistribution rights.
10. Treat AI-generated hardware and firmware as drafts until independently reviewed and tested.
11. Do not fabricate a board until schematic, layout, BOM, footprints, thermal, and manufacturing checks are complete.
