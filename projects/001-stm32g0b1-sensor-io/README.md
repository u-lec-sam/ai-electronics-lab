# AEL-001 — STM32G0B1 Sensor & I/O Controller

**Status:** preliminary design brief  
**MCU target:** STM32G0B1CET6, LQFP48  
**Purpose:** general-purpose low-voltage controller for sensor, serial, and GPIO experiments.

## Planned functional blocks
- External regulated DC input (connector and protection TBD)
- 3.3 V logic rail (regulator TBD after current and thermal budget)
- MCU core, reset, boot configuration, and decoupling
- SWD programming/debug header
- UART console
- I²C sensor expansion
- SPI and GPIO expansion
- Optional CAN-FD transceiver in a later revision

## Deliverables planned
- Requirements and pin-allocation table
- Datasheet-backed schematic
- Native KiCad PCB
- BOM and manufacturing outputs
- MCU-specific firmware and repeatable CI build
- ERC/DRC and prototype validation records

## Not yet complete
No native KiCad schematic/PCB or flashable firmware is included yet. Component selection and exact pin mapping remain subject to datasheet review. Do not order a PCB from this preliminary brief.
