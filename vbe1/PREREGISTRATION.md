# Preregistration: VBE-1 — Verification-Before-Execution Boundary Characterization

**Title:** Hardware characterization of a proof-gated (verify-then-execute)
circuit boundary on IBM Quantum

**Author:** Derek Hone, Independent Researcher
**Date committed:** 2026-07-13 (this commit timestamp precedes job submission)

## Status and Scope
Standalone demonstration/characterization. **Not UIP Phase 2.** Uses known
techniques (mid-circuit measurement + dynamic-circuit feed-forward). No claim
of new physics. The purpose is to measure how reliably a
verify-then-execute boundary holds on current hardware, and to publish the
failure rate either way.

## Backend and Budget
- Backend: ibm_kingston (Heron r2), IBM Quantum open plan
- Budget: <= 2 minutes QPU
- Fallback: if ibm_kingston is unavailable, the least-busy open-plan Heron
  backend may be used; the substitution will be recorded in RESULTS.md.

## Design
- Qubit A = "authorization" qubit, Qubit P = "payload" qubit
- Gated circuit: prepare A in |0> (unauthorized) or |1> (authorized);
  mid-circuit measure A; apply X to P only if the measured result = 1
  (classical feed-forward); measure P.
- Four arms, 4096 shots each:
  - Arm 1 (authorized, gated): expect P = 1
  - Arm 2 (unauthorized, gated): expect P = 0 — DENY-leakage arm
  - Arm 3 (ungated control): X applied unconditionally — expect P = 1
  - Arm 4 (idle control): nothing applied — baseline P readout error

## Primary Metric
DENY-leakage rate L = P(payload fired | unauthorized) = fraction of Arm 2
shots with P = 1.

## Preregistered Prediction
From published calibration data, L should be explained by: readout error on A
(a 0 misread as 1 triggers the gate) + readout error on P + P decoherence
during feed-forward latency. Predicted window: **L <= 3%** given typical
Heron readout errors (~1-2%).

## Kill-Condition
If L > 3%, the claim "a verify-then-execute boundary holds at the
few-percent level on current hardware" is **falsified** for this device and
qubit pair. The result will be reported either way, same day, with raw
counts and job IDs published.

## Secondary Metric (report only)
ALLOW-fidelity = P(payload fired | authorized) = fraction of Arm 1 shots
with P = 1.

## Rules
1. One run. No retries, no qubit-shopping, no pos
