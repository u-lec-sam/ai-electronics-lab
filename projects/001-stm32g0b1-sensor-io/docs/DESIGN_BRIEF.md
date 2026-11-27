# AEL-001 Design Brief

## Objective
Develop a low-voltage sensor and I/O reference board around STM32G0B1CET6 (LQFP48). This is a general-purpose development board, not a safety-critical or mains-connected product.

## Preliminary requirements
| Block | Proposal | State |
|---|---|---|
| Input | External regulated DC input | Connector/voltage/current TBD |
| Logic | 3.3 V | Regulator and load budget TBD |
| MCU | STM32G0B1CET6 LQFP48 | Candidate selected |
| Debug | SWDIO, SWCLK, GND, VTref, NRST | Proposed |
| Console | UART TX/RX/GND | Proposed |
| Sensor bus | I²C SDA/SCL/3V3/GND | Proposed |
| Expansion | SPI and GPIO | Proposed |
| CAN-FD | Optional add-on | Deferred |

## Required decisions before schematic capture
1. Choose input connector and specify allowed input range.
2. Set maximum board current and 3.3 V load budget.
3. Select regulator after checking current, dropout, stability, thermal dissipation, and capacitor requirements.
4. Define reverse-polarity, overcurrent, ESD, and transient protection.
5. Confirm every MCU pin and alternate function against the exact package datasheet.
6. Decide oscillator and RTC requirements.
7. Select connector pitch, board outline, mounting holes, and assembly constraints.

## Pin planning policy
Do not freeze physical pin numbers until the exact symbol and package pinout are cross-checked. Reserve debug, reset, boot, oscillator, and analog-sensitive pins before assigning expansion signals.

## Verification gates
- G1: datasheet-backed power tree and pin map
- G2: schematic ERC
- G3: PCB DRC and footprint review
- G4: power and thermal review
- G5: prototype bring-up and firmware smoke tests
- G6: manufacturing package review

## Manufacturer references
- Product page: https://www.st.com/en/microcontrollers-microprocessors/stm32g0b1ce.html
- Datasheet: https://www.st.com/resource/en/datasheet/stm32g0b1ce.pdf
