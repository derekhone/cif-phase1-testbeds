# Preregistration H2a-M: Echo-Protected Fixed-Point Test on IBM Quantum

Date: 2026-07-13  
Committed before hardware execution.

## Purpose

This test follows the prior Phase 1 IBM Quantum hardware tests and is being preregistered before executing Part B on hardware.

The test evaluates whether the echo-protected fixed-point prediction holds on IBM Quantum hardware using the backend and calibration selected by the script before execution.

## Backend and Calibration

Backend selected by script: ibm_marrakesh  
Qubit selected by script: qubit 2  
T2(echo): 431.5 us

## Prediction

Using the published calibration T2(echo), delay = 40 us, gain f = 0.5, and the same fixed-point formula used in the prior H2a script:

Predicted steady-state D* = 0.0407

Preregistered pass window: D* in [0.0366, 0.0447]

## Kill-condition

Measured steady-state D* outside the preregistered +/-10% window [0.0366, 0.0447] is a FAIL.

If the result falls inside the window, the test is recorded as PASS.

If it falls outside the window, the test is recorded as FAIL.

No post-hoc parameter adjustment counts as a result.

## Interpretation

A PASS supports the echo-protected fixed-point prediction under this specific hardware/calibration condition.

A FAIL further supports the conclusion that the simple two-parameter fixed-point law is not a reliable hardware law without additional terms for gate error, readout error, T1, refocusing limits, and hardware-specific aggregate loss.

Either outcome will be published and archived.
