# Appendix G — UIP v4: Inaccessible-Memory Chain Experiment
Date run: 2026-07-15 · Status: PREREGISTERED, EXECUTED, FALSIFIED

## Preregistration
System: 3 qubits A → M → B. Partial-SWAP coupling A↔M (R1=0.30) and M↔B (R2=0.30).
Independent dephasing on all three (γA=0.06, γM=0.06, γB=0.015). Recirculation
correction toward |+⟩ allowed ONLY on A and M — B is untouchable. Budget: one
correction per cycle. T = 200 cycles.

Policy under test (uip_v4): correct the qubit with larger deliverable inheritance
toward B: I2(A) = R1·R2·C(A)·τ², I2(M) = R2·C(M)·τ.
Baselines: always-A, always-M, alternating, random.

Predictions:
- P1: with noise attack alternating between A and M, uip_v4 beats all baselines in mean C(B).
- P2: under static noise, uip_v4 within 3% of best static baseline.
- Falsification: uip_v4 underperforms any baseline by >5%.

## Results
| Policy    | Mean C(B), attack | Mean C(B), static |
|-----------|-------------------|-------------------|
| always-A  | 0.2664            | 0.4571            |
| always-M  | 0.3742            | 0.4606            |
| alternate | 0.4431            | 0.6145            |
| random    | 0.4145            | 0.5854            |
| uip_v4    | 0.3742            | 0.4606            |

- P1: FAIL (−15.54% vs alternating baseline)
- P2: FAIL (−25.04% vs best static baseline)
- Preregistered falsification condition met: FALSIFIED.

## Diagnosis
The chain-discounted inheritance rule collapsed into "always correct M" (identical
numbers in both regimes) — the R1·R2 discount meant A almost never won the comparison,
so the policy was never adaptive. The alternating baseline dominated because chain
transport is a pipeline-maintenance problem: both links require periodic refreshing,
and greedy single-target rules starve one link.

## Conclusion
Third consecutive falsification (Appendices B, F, G) of inheritance-guided control,
including its most favorable setting (inaccessible target). The UIP inheritance
quantity, in every form tested, does not predict optimal correction allocation.
Simple resource-spreading policies dominate. Appendix A (single-qubit recirculation)
remains the framework's only pass.

## Methodological note
Predictions P1/P2 were specified before execution but not publicly timestamped prior
to the run. This commit establishes the record; future experiments adopt a
commit-preregistration-first workflow.
