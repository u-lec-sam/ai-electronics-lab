# AEL-002 architecture and benchmark study

- Date: 2026-11-27
- Branch: agent/ael-002-48v-modular-servo-brief
- Baseline commit: 6ca4716de7ae11e82e23ad2f61271dc9e4d1e899
- Status: preliminary research and requirements capture; not a hardware design release

## Problem

The repository's active queue contained only AEL-001. The user requested a general-purpose modular servo-drive workstream benchmarked against LS Mecapion iX7, with a safe low-voltage single-axis first prototype.

## Hypothesis

A narrowly bounded 24–48 VDC one-axis prototype, with control/power functional partitioning and explicit feedback/protection abstractions, can establish reusable servo-drive architecture without prematurely committing to mains power, current ratings, encoder universality, or an industrial fieldbus stack.

## Evidence gathered

- LS Mecapion's current public drive listing distinguishes iX7NH from iX7M: iX7NH is a network servo family across AC input variants; iX7M is a 200–240 VAC multi-axis EtherCAT family.
- EtherCAT Technology Group's iX7NH listing documents multiple encoder families and control cycle figures (position 125 µs, speed 62.5 µs, current 31.25 µs).
- TI's C2000 Motor Control SDK documents F28003x sensored FOC, encoder/Hall support, multiple current sensing methods, and a servo-drive-with-CAN example.
- ST documents a parallel STM32 motor-control ecosystem with PMSM/BLDC FOC and low-voltage evaluation support.

## Candidate change

Add AEL-002 as a preliminary project brief, record benchmark sources and safety/requirements boundaries, and reprioritize the single active task to resolve the motor/supply/load requirements and verify a C2000 evaluation path.

## Expected benefit

Create a traceable servo-drive workstream and prevent premature selection of power devices, ratings, encoder protocols or industrial safety claims.

## Tests and outcomes

- Live repository/protocol/state read: completed.
- Latest main CI run #35: success. Scaffold validation, contract tests and C syntax check passed. KiCad install/ERC/DRC steps were skipped because no native KiCad files exist.
- Documentation link/source review: recorded in the AEL-002 brief.
- Candidate branch CI: pending at record creation.

## Risks and limitations

No motor or encoder has been selected. No current/power/torque/speed/thermal rating is assigned. No native KiCad, firmware, simulation, HIL, bench or safety certification evidence exists. The 48 V nominal bus requires explicit regenerative-energy and overvoltage handling.

## Decision

Needs CI evidence and independent engineering review before integration. The document is a concept/preliminary brief only.

## Next experiment

Resolve the minimum motor/supply/load requirements and compare exact C2000 F280039C versus STM32G4 evaluation hardware before freezing the control MCU or power-stage envelope.
