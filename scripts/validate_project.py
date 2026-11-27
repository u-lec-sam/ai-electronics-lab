#!/usr/bin/env python3
import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
required = [
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/ENGINEERING_RULES.md",
    "projects/001-stm32g0b1-sensor-io/docs/DESIGN_BRIEF.md",
    "projects/001-stm32g0b1-sensor-io/hardware/BOM_DRAFT.csv",
    "projects/001-stm32g0b1-sensor-io/hardware/INTERFACE_PLAN.csv",
    "projects/001-stm32g0b1-sensor-io/firmware/src/main.c",
]
missing = [p for p in required if not (root / p).is_file()]
if missing:
    raise SystemExit("Missing files: " + ", ".join(missing))

for rel in required:
    if rel.endswith(".csv"):
        with (root / rel).open(newline="", encoding="utf-8") as f:
            if len(list(csv.reader(f))) < 2:
                raise SystemExit(f"CSV has no data rows: {rel}")

print("Scaffold validation passed.")
print("No KiCad ERC/DRC or target MCU firmware build is claimed by this check.")
