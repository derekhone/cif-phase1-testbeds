# Replication Note: H2a-M Fixed-Point Law on ibm_marrakesh

**Status:** Replication of an already-falsified law. The fixed-point law was
falsified on ibm_kingston (Appendix I, 81.9% deviation) and remains falsified
regardless of this outcome. This run tests device-dependence only.

**Preregistration:** commit `prereg_h2a_marrakesh` (committed before job submission)

## Run details
- Backend: ibm_marrakesh (Heron), qubit 2
- T2(echo): 431.5 µs
- Job ID: d9airde6hjac73fegau0
- Date: 2026-07-13

## Preregistered prediction
- Predicted D* = 0.0407, pass window [0.0366, 0.0447]

## Result: FAIL
- Measured D* = 0.0529
- Deviation: 30.1% (outside ±10% window)

## Interpretation
- The falsification is not device-specific: kingston 81.9% off, marrakesh 30.1%
  off. Two devices, same verdict — the two-parameter law underpredicts
  steady-state drift on hardware.
- Deviation range across devices: 30–82%.
- Post-hoc note (zero evidential weight): deviation shrank on the
  higher-quality qubit, consistent with the Appendix I attribution that omitted
  gate/readout/T1 terms drive the residual gap. This informs the Phase 2
  extended-model hypothesis but proves nothing here.

Ledger unchanged: 4 confirmed / 5 falsified. This note strengthens
falsification #5; it does not reopen Phase 1.
