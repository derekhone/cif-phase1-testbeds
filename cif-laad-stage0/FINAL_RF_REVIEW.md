# CIF-LAAD - Final RF Adversarial Review

Written for Remnant Fieldworks by the same standard applied to every RF
deliverable: truth over flattery. Scores are defended with measured numbers
from `experiments/EXPERIMENT_LEDGER.md`, `bench/BENCHMARK.md`, and
`security/SECURITY.md`. Nothing here is rounded up to feel better.

---

## Scorecard (0-100 per axis)

| Axis | Score | Defense of the score |
|---|---|---|
| Science | 70 | Fair shared-filter baseline, 25 seeds, all RNG seeded, negatives preserved, hypotheses falsifiable. Loses points only because everything is synthetic - no real data yet. |
| Engineering | 60 | Clean, modular, runs end-to-end, reproducible by one command each. Held back by pure-Python single-thread scaling (10 Hz to ~25-30 tracks) and unbounded evidence growth (rotation not yet built). |
| Novelty | 45 | The primitives (NIS health, label voting, modality count, coasting) are all standard and we say so. The genuine contribution is the composition + preserved contradictions + tamper-evident binding. Real but modest; not a new estimator. |
| Defense relevance | 40 | One real, mission-relevant capability (continuity through dropout) and clean C2 boundary. Capped hard by the heavy-clutter regression - clutter IS the low-altitude mission. |
| Commercial potential | 35 | Honest status is RESEARCH ONLY: zero hardware, zero independent validation. There is a credible, cheap path (software fixes then recorded-data run), which is the only reason it is not lower. |
| Evidence quality | 85 | The strongest axis. Every claim traces to a reproducible number; failures and regressions are documented as prominently as wins. This is the RF standard done right. |
| Integration readiness | 65 | Documented observation/track/evidence contracts, JSON schemas validated against real samples, adapter pattern, ExecutionProof handoff clearly labeled a stub. |

**Overall: 57 / 100.** A strong, honest research prototype with one real
capability and one disqualifying-for-mission weakness. Not a product, not a
fraud - exactly what a fast falsification project should produce.

---

## Ten questions, answered straight

**1. Is CIF-LAAD real or theatre?** Real. It runs, it is measured against a
fair baseline, and its failures are on the record. It is not a product.

**2. Does CIF produce measurable value beyond ordinary fusion?** Yes, narrowly:
continuity through total dropout (1.0 vs 0.3), fewer ID switches and false
tracks in dense scenes, and auditable provenance. No on accuracy, calibration,
or clutter.

**3. What is the single best result?** Track survival through a total sensor
dropout with no reacquisition gap, vs 4.02 s for the baseline. Decisive in sim.

**4. What is the worst, most damaging finding?** Heavy-clutter regression:
worse RMSE, worse continuity, and MORE false tracks than the baseline.
Inheritance re-links to clutter. This is disqualifying for the mission until
fixed.

**5. Is any RF claim currently overstated?** No, provided we hold to
`docs/03_CLAIM_DISCIPLINE.md`. The trap to avoid is claiming
"better-calibrated uncertainty" - the NEES data does NOT support it.

**6. Would a defense engineer take a meeting after seeing this?** For a scoped
data run on dropout continuity + evidence, plausibly yes. For a pilot or
purchase, no - and we should not ask.

**7. What is the honest TRL and status?** TRL 3, RESEARCH ONLY. Zero hardware,
zero independent validation.

**8. What is the cheapest next step that could kill or advance it?**
Coherence-gated inheritance + a MOTA/MOTP/OSPA re-run + one recorded-data
replay. All software, all fundable internally. If clutter is not bounded,
escalate the kill decision.

**9. Should RF spend more on this?** Yes, but only the 30/60-day software
plan. No radar purchase, no prime pitch, no hardware capital until the Stage 0
recorded-data result exists.

**10. Does this uphold the RF standard ("claims kept narrower than the
evidence")?** Yes. The evidence is real, the negatives are kept, the language
is disciplined, and the boundary (sense -> evidence, never authorize/execute)
is intact. Built in faith, tested in public, claims kept narrower than the
evidence.

---

## One-line verdict

Keep it alive as research; fix the clutter regression before any mission
language; earn hardware and a customer with a recorded-data run, not a pitch.

---

## Addendum - coherence-gated inheritance experiment (result)

The pre-committed "coherence-gated inheritance" next step has now been run
(25 seeds, identical seeds across modes; see
`docs/07_COHERENCE_GATED_INHERITANCE.md`). Honest outcome:

- The pre-registered coherence gate (tighter re-link gate + >= 2 corroborators)
  was **falsified**: it made the clutter and dense regressions WORSE, not
  better, because genuine single-sensor re-links failed the gate, expired, and
  respawned as fresh tracks.
- The change that DID help was batching inheritance (one coasting id absorbs
  all its gated obs per cycle). It cut clutter false-track frames from 103 to
  15 (below the baseline's 76), improved continuity, cut ID switches, and
  PRESERVED the dropout win (continuity 1.0 vs 0.3). It is now the default.
- The **position-RMSE regression under clutter/dense is still NOT fixed**
  (~25-33 m vs baseline ~6 m). The A4 kill criterion is only partially met:
  false-track/continuity bounded, RMSE not. The overall verdict below is
  unchanged - this is still research, not a mission claim.
