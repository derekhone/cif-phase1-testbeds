# Preregistration H2a: Echo-Protected Fixed-Point Test on IBM Quantum

Date: 2026-07-11 (committed BEFORE execution)
Follows from Appendix H (H1: FAIL, 383.7% deviation, diagnosed as T2 vs T2* input error).

## Hypothesis
The Appendix A steady-state fixed-point law holds on a real transmon qubit
when the governing decay rate matches the published calibration. To achieve
this, an X (echo) pulse is inserted at the midpoint of each idle delay, so
the delay decays at echo-T2 — the quantity IBM actually calibrates.

Prediction machinery is IDENTICAL to H1:
  gamma = delay / T2_echo
  C* = f / (1 - (1-f) * exp(-gamma)),  D* = (1 - C*)/2
with f = 0.5, delay = 40 us per cycle, 8 cycles, steady state = mean of last 3.

## Kill-condition
Measured steady-state D* outside +/-10% (relative) of the prediction computed
in Part A (from that day's calibration T2 of the selected qubit) => FAIL.
Reported either way as Appendix I.

## Interpretation rules
- PASS: fixed-point law confirmed on hardware once the input rate is honest.
- FAIL: the law itself (not merely its inputs) is falsified on hardware.
- No post-hoc parameter adjustment counts as a result.
