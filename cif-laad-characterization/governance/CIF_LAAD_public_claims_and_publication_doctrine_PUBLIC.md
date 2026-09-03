# CIF-LAAD: Public Claims and Publication Doctrine

**Prepared:** 2026-09-02
**Status:** Public governance statement for the CIF-LAAD characterization package. It sets out (a) the public claims Remnant Fieldworks stands behind, (b) the two-layer public/controlled publication model, (c) the controlled-access statement, and (d) the access-request policy.

---

## Part A: Public claims (earned envelope)

Every claim below is bounded by what the six-document record actually supports. Each is tagged VALIDATED (supported by the evidence), FALSIFIED/LOSS (a preserved negative result we state openly), or BOUNDARY (a scaling limit, never a win). Simulation only, TRL 3, no hardware, no real sensor data.

### VALIDATED (we will claim these)

1. **Sensor-dropout continuity.** Across an external-library comparison, CIF-LAAD maintains track continuity through a total sensor blackout (dropout continuity 1.000) where both Stone Soup GNN and Stone Soup JPDA drop to 0.200. This is the structural property CIF-LAAD was built for. (EXP-9, EXP-14)
2. **False-track suppression under clutter and density.** CIF-LAAD produces far fewer false-track frames than either external tracker at scale: heavy_clutter 3.6 vs JPDA 435.6 and GNN 516.8 (about a 120x reduction); many_targets_6 28.8 vs 146.6 and 165.6. This holds against both comparators. (EXP-9, EXP-14)
3. **Compute cost.** CIF-LAAD is the fastest of the three trackers in every fixed scenario (1.6x to 30x), and in the scaling study it stays within both operational budgets (500 ms/2 Hz and 100 ms/10 Hz), even at p95, across the entire swept range (up to N=32 targets and clutter_rate=32), while both external trackers reach a hard 300 s per-seed time cap at N=8 and clutter=4. Stated as a computational-tractability result only. (EXP-9, EXP-14, EXP-15)
4. **Contested-geometry bounded advantage.** In crossing_two, CIF-LAAD is best on all four metrics simultaneously (RMSE, continuity, false tracks, ID switches). The advantage is modest but consistent. (EXP-9, EXP-14)
5. **Tamper-evident provenance.** The evidence chain is tamper-EVIDENT (not tamper-proof) under the tested tamper operations. (EXP-6, master series)
6. **Architectural boundary.** CIF-LAAD stops at evidence handoff. It does not perform targeting, engagement, jamming, spoofing, weapons authorization, or autonomous defeat. This is a design-scope statement, verifiable from the architecture.

### FALSIFIED / LOSS (we will state these openly, unsoftened)

7. **Positional accuracy is not a CIF-LAAD strength.** Both external trackers achieve lower positional RMSE than CIF-LAAD in 5 of 6 scenarios; CIF-LAAD wins RMSE only in crossing_two. In clean and dropout conditions JPDA tracks position more tightly (sensor_dropout 5.94 vs 9.39 m, p=0.0001). (EXP-9, EXP-14)
8. **RMSE-at-scale weakness.** Under heavy clutter and many targets CIF-LAAD RMSE is roughly 23 to 24 m vs 5 to 10 m for the external trackers. This is a genuine, structural degradation mode (the price of continuity and false-track suppression), documented and diagnosed, not a tuning bug. (EXP-9, EXP-10)
9. **The low-q remediation carries a real cost and was not adopted.** Lowering process noise (q=2.0) improves RMSE about 10% but significantly increases identity_conflict false tracks (p=0.035). It was recorded as ADOPT-WITH-DOCUMENTED-COST and NOT adopted; q=8.0 remains the frozen default. (EXP-11 Part A)
10. **Two candidate improvements were rejected.** The v2 cross-target fold filter (EXP-11 Part B) and the adaptive-q controller (EXP-12) were both REJECTED against pre-registered kill criteria and are preserved as labeled failures. (EXP-11, EXP-12)
11. **The coherence-gate inheritance mode is falsified** and kept in the record as not recommended. (master series)
12. **ID stability is bounded.** CIF-LAAD has more ID switches than JPDA in benign scenes (clean_single 3.5 vs 0.0). Its ID-stability advantage is bounded to low target density. (EXP-14, master series)

### BOUNDARY (scaling limits, never stated as wins)

13. **Comparator timeouts are scaling boundaries.** When GNN and JPDA hit the 300 s time cap, that is a limit of those trackers on this hardware, not a CIF-LAAD performance win. Reported as a boundary. (EXP-15)
14. **CIF-LAAD quality degrades with load.** Completing every compute point does not mean tracking it well: RMSE roughly quadruples from N=2 to N=32 (10.3 to 40.4 m) and continuity collapses to 0.019 under the heaviest clutter. Compute tractability does not extend to accuracy at scale, and we make no such claim. (EXP-15)
15. **The contamination/measurement-cleanliness finding is a hypothesis, not a proof.** The corrected large-N timings are the clean numbers of record; the earlier inflated figures are superseded and should not be cited. This is a measurement correction, not a CIF-LAAD win. (EXP-15)

### Required framings (verbatim guardrails)

- Say CIF-LAAD "remains computationally tractable across the tested range while its own tracking quality materially degrades with load," NOT "scales to 32 targets."
- Comparator timeouts are "scaling boundaries," never CIF-LAAD wins.
- "JPDA achieves lower positional RMSE than CIF-LAAD in 5 of 6 tested scenarios."
- The measurement-cleanliness note is "a strongly supported hypothesis, not a proven mechanism."
- Every win is reported with its cost in the same breath (continuity/false-track wins come with an RMSE-at-scale loss).
- Every claim carries: simulation only, TRL 3, no hardware, no real sensors.

---

## Part B: Two-layer publication model (public science, controlled implementation)

Remnant Fieldworks publishes under a two-layer model. The irreversibility asymmetry drives it: publishing runnable code cannot be undone, withholding it can be relaxed later.

**Publish order:**

1. **Zenodo research record** (DOI-minted, citable): papers/results, preregistrations (public form, see below), aggregate results tables, provenance/manifests, limitations. Carefully selected non-operational artifacts only.
2. **Public GitHub research packet:** README, methodology at a reproducible-but-not-operational level, results tables, provenance/hashes, limitations, high-level architecture, the controlled-access statement, and the access-request path. No runnable engine.
3. **Private controlled code repository:** the runnable engine, ciflaad_v2/, all tuned internals and parameter tables, adversarial/scenario-generation harnesses at deployment-relevant fidelity, and any future real-sensor adapters or defense-specific integration. Access granted individually after screening.
4. **Sites (ExecutionProof, Remnant Fieldworks):** link only to the public science, carry the controlled-access statement, and provide the reviewer contact path.

**Preregistration nuance:** publish preregistrations in a lightly redacted public form (research question, hypotheses, criteria, seed counts, comparator identity, budgets) to preserve the timestamped falsifiability, while keeping exact scenario-generation code and any parameter table that functions as a build recipe in the controlled repo. The package manifest tags each artifact so borderline ones can be decided individually.

---

## Part C: Controlled-access statement (for the public repo and sites)

> Research characterization materials for CIF-LAAD are public: research questions, preregistrations, methods at a reproducible-but-not-operational level, aggregate results, external comparator findings, preserved failures, limitations, and integrity manifests. The runnable implementation is access-controlled while Remnant Fieldworks evaluates security, dual-use, and applicable export-control obligations. CIF-LAAD is research-only and simulation-only (TRL 3). It performs evidence fusion and track characterization and stops at evidence handoff. It does not perform targeting, engagement, jamming, spoofing, weapons authorization, or autonomous counter-UAS action, and it does not authorize or execute any such action. Requests for implementation access from university researchers, government evaluators, and prospective research or defense partners are considered individually, subject to Remnant Fieldworks' review.

This statement does not state or imply that CIF-LAAD has been determined to be ITAR-controlled, EAR-controlled, or subject to any specific export-control classification. It states only that access is controlled pending Remnant's own security, dual-use, and applicable export-control review.

---

## Part D: Access-request policy

1. **Who may request:** named university researchers, government evaluators, and prospective research/defense partners, as identified individuals or entities.
2. **What the requester provides:** identity and affiliation, intended use, and citizenship/entity nationality sufficient to assess export-control screening needs.
3. **Mandatory gate before any implementation access to a defense contractor, foreign person or entity, or overseas researcher:** screening by qualified export-control counsel of exactly what is being shared. No ITAR, EAR, or other export-control determination is stated or implied by this policy; the screening exists because Remnant is evaluating its applicable obligations, not because it has concluded any specific classification applies.
4. **What is shared and how:** access to the private repository is granted per-approval, scoped to what the reviewer needs, logged with date and recipient.
5. **What is never in public artifacts:** no real secret, key, credential, or deployment recipe appears in any public file; borderline artifacts are held in the controlled repo per the manifest tags.
6. **Records:** maintain an access log (who, when, scope, screening outcome) so provenance of implementation sharing is auditable.

---


## Publication order

Publication proceeds in a fixed order: the Zenodo research record first, then the public GitHub research packet, then the private controlled code repository behind the access gate, then the public sites. Every stage is gated on explicit internal approval.

*(Internal review notes have been omitted from this public version.)*
