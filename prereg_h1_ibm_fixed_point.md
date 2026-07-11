# Preregistration H1: Hardware fixed-point test (IBM Quantum)

Date: 2026-07-11 (committed before any hardware run)

## Hypothesis
The Appendix A steady-state drift fixed point holds on a real transmon qubit:
using the device's calibrated T2 and the circuit cycle duration, compute the
per-cycle dephasing gamma_hat, predict D* analytically via the Appendix A
fixed-point equation (gain g = 0.5), then measure the steady-state drift after
N = 8 correction cycles on hardware.

## Kill-condition
Measured steady-state D* outside +/-10% (relative) of the analytic prediction
=> FAIL, reported as Appendix H regardless of outcome.
(Window is wider than simulation's 2% due to SPAM error and device drift.)

## Method
- Backend: least-busy available IBM Quantum device
- Target state |+>; correction = partial re-preparation with f = 0.5,
  implemented as probabilistic reset-and-reprepare (classical mixing across shots)
- gamma_hat from IBM's published calibration T2 (no QPU cost) + known delay per cycle
- 4096 shots per circuit; X-basis measurement gives coherence C = |<X>|;
  cross-checked with Z-basis for full drift estimate
- One job, ~9 circuits (cycle 0..8). Estimated QPU time: under 3 minutes.
