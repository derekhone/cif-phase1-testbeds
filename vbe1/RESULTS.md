# VBE-1 Results: FAIL (kill-condition triggered)

- Backend: ibm_kingston, 4096 shots/arm, Job ID: d9ajf3eg26ic73deq3l0
- Preregistered kill-condition: DENY-leakage L <= 3%
- Measured L = 12.62% -> FAIL. The claim "a verify-then-execute boundary holds at the few-percent level on current hardware" is falsified for this device/qubit pair.

## Arm results (fraction of shots with payload = 1)

- Arm 1: authorized, gated (ALLOW-fidelity): 0.9014
- Arm 2: unauthorized, gated (DENY-leakage): 0.1262
- Arm 3: ungated control: 0.9402
- Arm 4: idle control (baseline readout): 0.1350

## Post-hoc note (zero evidential weight)

The idle control (13.5%) is statistically indistinguishable from the DENY-leakage (12.6%): the leakage is dominated by raw readout/initialization error on the payload qubit, not by the feed-forward gate misfiring. The boundary mechanism appears sound; the certification floor on this qubit pair is set by measurement noise an order of magnitude above the preregistered 1-2% assumption. A revised test would require preregistered qubit selection by calibration data and/or readout error mitigation - not run today.

## Ledger note

One run, no retries, as preregistered. A stray character pasted into the script caused a crash after results printed but before the JSON auto-saved; the JSON committed here is transcribed from the printed output (screenshot retained).
