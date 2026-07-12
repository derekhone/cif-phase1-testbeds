# UIP Phase 1 Testbeds — PHASE 1 CLOSED

**Status: PHASE 1 CLOSED (July 12, 2026).** Candidate framework — not claimed as new physics. All results are consistent with standard quantum mechanics, quantum information theory, and feedback control. Final ledger: **4 confirmed / 5 falsified**, including two preregistered hardware rejections on IBM Quantum, both published unedited the same day. The "Unified" designation was retired by the Appendix G result. This repository exists so reviewers can reproduce, vary, and attempt to break every reported result.

**Preprint (DOI, all versions):** https://doi.org/10.5281/zenodo.21246246

## Method

Every test in this program followed the same protocol:

1. Hypothesis and numerical kill-condition preregistered (committed publicly) before execution
2. Test executed exactly as specified
3. Outcome published same day, pass or fail
4. Post-hoc analyses labeled as such and given zero evidential weight
5. Failed claims retired or sharpened into new preregisterable hypotheses — never silently retried
6. Strict no-third-attempt rule on every falsified claim within Phase 1

## Final Ledger

| Appendix | Claim tested | Outcome |
|----------|--------------|---------|
| A | Single-qubit recirculation fixed point (simulation) | **PASS** (steady-state drift predicted within 2%) |
| B (v1, v2) | Inheritance-guided two-qubit control beats static baselines | **FAIL** (x2) |
| C | Advantage exists under restricted target access | **PASS** |
| D–E | Quantitative crossover law s\*(gamma) | **PASS** |
| F | Near-optimality of the heuristic (gap <= 5%) | **FAIL** (12.19%) |
| G | Universality ("Unified") | **FAIL — "Unified" retired** |
| H | Fixed-point law, calibration inputs, IBM hardware | **FAIL** (383.7%) |
| I | Fixed-point law, echo-protected, IBM hardware | **FAIL** (81.9%) — law itself falsified |

**FINAL: 4 confirmed / 5 falsified. Both hardware verdicts were delivered by a device outside our control and published unedited the same day. Phase 1 closed under the no-third-attempt rule.**

## Hardware tests (IBM Quantum, ibm_kingston, Heron r2, qubit 140)

The fixed-point law under test: `C* = f / (1 - (1-f) * exp(-gamma))`, `D* = (1 - C*) / 2`, with `gamma = delay / T2`.

**Appendix H (H1)** — bare idle delays, decay rate from published calibration T2 (job `d99brisqp3as739tudkg`):

- Predicted D\* = 0.0302 (±10% window). Measured D\* = 0.1463 — deviation **383.7% — FAIL**
- Diagnosis: published T2 is echo-T2; bare idles decay at T2\* (5–10x shorter). Input model falsified.

**Appendix I (H2a)** — X echo at midpoint of every idle, preregistered in `prereg_h2a_echo_fixed_point.md` with the escalation clause that failure falsifies the law itself, not merely its inputs (job `d99h2nd2su3c739keu80`):

- Predicted D\* = 0.0302 (±10% window [0.0272, 0.0333]). Measured D\* = 0.0550 — deviation **81.9% — FAIL. The law itself is falsified on hardware.**
- The H1 diagnosis was substantially correct: echoes cut the error ~5x (383.7% → 81.9%). Residual gap attributed (zero evidential weight) to gate error, readout error, single-echo refocusing limits, and T1.
- What survived both runs: the qualitative fixed-point structure — fast convergence to a flat, stable coherence plateau — exactly as the recirculation model predicts, but at a level set by the device's true aggregate loss.

Final status of the law: **a simulation result, not a hardware law.** An extended model with explicit gate-error, readout-error, and T1 terms is a Phase 2 hypothesis, deliberately not attempted in Phase 1.

## Contents

- **uip_phase1_complete_synthesis_final.pdf** — Final closing manuscript (Appendices A–I): 4 confirmed / 5 falsified. Supersedes all earlier synthesis drafts.
- **appendix_a_qubit_testbed.py** — Appendix A: single-qubit recirculation fixed point (PASS)
- **appendix_b_inheritance_test.py** — Appendix B: inheritance-guided control (FAIL x2)
- **appendix_c_restricted_access_test.py** — Appendix C: restricted-access advantage (PASS)
- **uip_phase1_appendix_de_crossover.pdf** — Appendices D–E: crossover law s\*(gamma) (PASS)
- **uip_phase1_appendix_f_gauntlet_failure.pdf** — Appendix F: optimal-policy gauntlet (FAIL, 12.19%)
- **uip_phase1_appendix_g_universality.pdf** — Appendix G: universality test (FAIL; "Unified" retired)
- **h1_ibm_fixed_point.py / prereg_h1_ibm_fixed_point.md / uip_phase1_appendix_h_hardware_fail.pdf** — Appendix H: first hardware test (FAIL, 383.7%)
- **h2a_echo_test.py / prereg_h2a_echo_fixed_point.md / uip_phase1_appendix_i_h2a_hardware_result.pdf** — Appendix I: echo-protected hardware test (FAIL, 81.9% — law falsified)

## Reproducibility

All preregistration commits, scripts, raw cycle data, and IBM job IDs are in this repository. Anyone with a free IBM Quantum open-plan account can rerun both hardware tests:

    pip install qiskit qiskit-ibm-runtime
    python h1_ibm_fixed_point.py
    python h2a_echo_test.py

Refutations and tightenings are solicited as explicitly as confirmations — please open an issue.

## Citation

Hone, D. (2026). *A Preregistered Falsification Program for a Coherence-Inheritance Control Framework: Simulation Testbeds and Two Hardware Tests.* Zenodo. https://doi.org/10.5281/zenodo.21246246

License: CC-BY 4.0

---

*"A false balance is an abomination to the LORD, but a just weight is His delight." — Proverbs 11:1*
