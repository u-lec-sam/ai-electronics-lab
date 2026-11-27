# Current Project State

**Snapshot date:** 2026-11-27  
**Repository:** `u-lec-sam/ai-electronics-lab`  
**Default branch at snapshot:** `main`  
**Status:** recursive-improvement memory/evaluation bootstrap passed CI on candidate branch; awaiting integration.

## Verified repository state

- Public GitHub repository; connected GitHub integration has read/write permissions.
- MCU families in scope: STM32, TI MSPM0, C2000, MSP430, ESP32, and future profiles.
- Active hardware project: AEL-001, STM32G0B1CET6 LQFP48 sensor and I/O reference board.
- AEL-001 is a preliminary design brief only.
- No committed native KiCad schematic or PCB was present at the baseline inspection.
- Firmware is a portable C scaffold, not a flashable target image.
- CI has a scaffold validation job and conditional KiCad ERC/DRC steps; baseline KiCad files were absent.
- Latest inspected main commit at baseline: `ccdf16b1fbb3c1b594440d9f7ccc63e05c53b89e`.
- Six recent GitHub Actions runs were listed; the latest inspected run completed with conclusion `success` for that commit. This confirms the configured workflow completed, not electrical correctness.

## Open engineering decisions for AEL-001

1. Input connector, voltage range, and maximum input current.
2. Board current budget and 3.3 V load budget.
3. Regulator selection and thermal/power analysis.
4. Reverse-polarity, overcurrent, ESD, and transient protection.
5. Exact MCU pin and alternate-function allocation from the LQFP48 datasheet.
6. Oscillator/RTC requirements.
7. Connector pitch, board outline, mounting, and assembly constraints.

## Latest scaffold improvement

- Candidate branch: `agent/recursive-evaluation-bootstrap`
- Candidate commit: `558fcbaa3fbb7c5c8dd0ed7a4a8f57084861ab49`
- GitHub Actions run 19: success.
- Repository-contract tests, scaffold validation, and C syntax check: passed.
- KiCad checks: skipped because no native KiCad files exist.
- Pull request: https://github.com/u-lec-sam/ai-electronics-lab/pull/1

## Next actions

1. Integrate the tested scaffold improvement.
2. Research the exact STM32G0B1CET6 package pinout and power requirements.
3. Produce a traceable pin-allocation proposal and power-tree design before schematic capture.

## Confidence and limitations

This snapshot is a dated summary, not a substitute for live repository reads. Refresh it from GitHub before relying on it. No schematic, PCB, firmware build, or hardware measurement is claimed.
