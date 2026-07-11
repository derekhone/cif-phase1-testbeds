# UIP Phase 1 — Numerical Testbeds

Reproducible simulations accompanying the UIP Phase 1 review packet.

**Status:** Candidate framework under review. Not claimed as new physics. All results are consistent with standard quantum mechanics, quantum information theory, and feedback control. This repository exists so reviewers can reproduce, vary, and attempt to break every reported result. Note: the "Unified" designation was retired by the Appendix G result (see below).

**Preprint (DOI):** https://doi.org/10.5281/zenodo.21246247

## Contents

- **appendix_a_qubit_testbed.py** — Single noisy qubit memory. Full numerical specification of C, D, R, U, G, L, W, E. Six falsification tests + fixed-point prediction. **Outcome: 6/6 PASS; predicted D* = 0.1032 vs simulated 0.1051 (within 2%)**
- **appendix_b_inheritance_test.py** — Two-qubit inheritance-guided control (v1 and v2, preregistered). **Outcome: FAIL — reported in full**
- **appendix_c_restricted_access_test.py** — Preregistered v3 test: inheritance-guided control when the target CANNOT be corrected directly. **Outcome: ROBUST PASS at weak coupling (+3.5% over best baseline, 95% CI excludes zero, N=100 seeds); loses at strong coupling**
- **uip_phase1_appendix_de_crossover.py** — Crossover point + zero-free-parameter law s*(γ), r = 0.976; 3-qubit generalization. **Outcome: CONFIRMED**
- **uip_phase1_appendix_f_gauntlet.py** — Optimal-policy gauntlet: decision-quantity sufficiency (v3: 12.19%, v4: 22.06%). **Outcome: FALSIFIED (twice)**
- **uip_phase1_appendix_g_universality.py** — Cross-platform transfer of C̄* = 1/1.45 to a structure-matched classical system. **Outcome: FALSIFIED — "Unified" retired**
- **uip_phase1_synthesis_manuscript.pdf** — Complete Phase 1 manuscript: 4 confirmed predictions, 3 falsified claims. **FINAL**

## Why the failures are included

The Phase 1 commitment is that UIP claims be falsifiable and that falsifications be published alongside confirmations. Appendix B narrowed the inheritance claim to a boundary hypothesis (restricted-access systems), confirmed in Appendix C. Appendices F and G closed the control-sufficiency and universality claims at their preregistered thresholds. No claim was revised more than once; iteration beyond that was prohibited to avoid curve-fitting.

## Reproducing

    pip install numpy scipy
    python appendix_a_qubit_testbed.py
    python appendix_b_inheritance_test.py
    python appendix_c_restricted_access_test.py
    python uip_phase1_appendix_de_crossover.py
    python uip_phase1_appendix_f_gauntlet.py
    python uip_phase1_appendix_g_universality.py

Deterministic up to seeded RNGs. Reviewers are invited to vary noise rates, gain, sensing noise, coupling strength, and envelope parameters.

## Open falsification invitation

If you can break tests T1–T6 in Appendix A, break the s*(γ) law outside the swept range, tighten the Appendix F adversary (exact dynamic programming widens our reported gap), or find a classical system with a native correction cost showing a crossover at C̄* = 1/1.45 — please open an issue. Refutations are as valuable as confirmations.

## Appendix H — First Hardware Test (IBM Quantum): FAIL

First test outside our own simulations. Preregistered in
`prereg_h1_ibm_fixed_point.md` before execution.

- Backend: ibm_kingston (Heron r2), qubit 140, job d99brisqp3as739tudkg
- Predicted steady-state D* = 0.0302 (from calibration T2, +/-10% window)
- Measured D* = 0.1463 — deviation 383.7% — **kill-condition triggered**
- Diagnosis: bare-idle decay is governed by T2*, not echo-T2 from published
  calibration; the fixed-point *structure* (flat steady state) was observed,
  but the input noise model is falsified on hardware.
- Sharpened hypothesis H2 (not yet run): same law with in-situ measured
  decay rate, or echo pulses inserted in delays.

Ledger: 4 confirmed / 4 falsified — including one rejection delivered by
hardware we do not control.
