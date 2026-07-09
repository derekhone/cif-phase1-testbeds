# UIP Phase 1 — Numerical Testbeds

Reproducible simulations accompanying the UIP (Unified Inheritance Physics)
Phase 1 review packet.

**Status:** Candidate framework under professor review. Not claimed as new physics.
All results are consistent with standard quantum mechanics, quantum information
theory, and feedback control. This repository exists so reviewers can reproduce,
vary, and attempt to break every reported result.

**Preprint (DOI):** https://doi.org/10.5281/zenodo.21246247

## Contents
File	Description	Outcome
appendix_a_qubit_testbed.py	Single noisy qubit memory. Full numerical specification of C, D, R, U, G, L, W, E. Six falsification tests + fixed-point prediction.	6/6 PASS; predicted D* = 0.1032 vs simulated 0.1051 (within 2%)
appendix_b_inheritance_test.py	Two-qubit inheritance-guided control (v1 and v2, preregistered).	FAIL — reported in full. Inheritance-guided allocation loses to direct target protection whenever the target is directly correctable.
Why the failure is included
The Phase 1 commitment is that UIP claims be falsifiable and that falsifications
be published alongside confirmations. Appendix B narrows the inheritance claim
and leaves a sharpened boundary hypothesis (restricted-access systems, v3)
open for independent testing. It was deliberately not tested by the authors
to avoid iterative revision converging on curve-fitting.

Reproducing
pip install numpy scipy
python appendix_a_qubit_testbed.py
python appendix_b_inheritance_test.py
python appendix_c_restricted_access_test.py
Deterministic up to seeded RNGs. Reviewers are invited to vary noise rates,
gain, sensing noise, coupling strength, and envelope parameters.

appendix_c_restricted_access_test.py - Preregistered v3 test: inheritance-guided control when the target CANNOT be corrected directly. ROBUST PASS at weak coupling (+3.5% over best baseline, 95% CI excludes zero, N=100 seeds); loses at strong coupling. First positive result for the inheritance quantity, reported with full boundaries.

Open falsification invitation
If you can break tests T1–T6 in Appendix A, or demonstrate a regime where the
v2 inheritance rule beats all baselines (contradicting our negative result),
please open an issue. Refutations are as valuable as confirmations.

"A false balance is an abomination to the LORD, but a just weight is His
delight." — Proverbs 11:1
