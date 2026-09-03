# CIF-LAAD

**Coherent Inheritance Framework for Low-Altitude Air Defense** - a
sensor-agnostic software fusion, tracking, and evidence layer.

> STATUS: RESEARCH ONLY. TRL 3. SIMULATION-ONLY. Zero hardware, zero real
> sensor data, zero independent validation. This is a fast falsification
> project - "does CIF produce measurable value beyond ordinary fusion?" - not
> a market entry. See `FINAL_RF_REVIEW.md` for the honest verdict.

## The one-paragraph truth

CIF-LAAD adds three things to an ordinary multi-sensor tracker: track
inheritance that survives total sensor dropout, a per-track coherence/confidence
signal that a contradiction can veto (fail-closed), and a tamper-evident
hash-linked evidence chain. In 25-seed simulation against a fair GNN baseline
sharing the same filter, it is DECISIVELY better on continuity through dropout
(1.0 vs 0.3), meaningfully better on identity-switch and false-track reduction
in dense scenes, NEUTRAL in benign scenes, and WORSE in heavy clutter (it
re-links to false alarms). It is never more accurate. The clutter regression is
a real, preserved liability in exactly the mission-defining regime.

## Layout

```
ciflaad/     core library (observation, kalman, correlation, evidence,
             coherence, confidence, track, fusion, baseline)
sim/         synthetic scenarios + metrics
experiments/ 25-seed comparison harness -> EXPERIMENT_LEDGER.md
bench/       latency/memory/overload -> BENCHMARK.md
security/    17-case adversarial harness -> SECURITY.md
api/         data contracts, JSON schemas, real sample JSON, adapter doc
docs/        hostile review, kill criteria, claim discipline, readiness,
             TRL/boundaries, customer reality test
customer/    technical-evaluation packet + per-org variants + pilot criteria
FINAL_RF_REVIEW.md   adversarial 0-100 review and verdict
```

## Reproduce everything

```
python -m experiments.run_experiments --seeds 25   # EXPERIMENT_LEDGER.md
python -m bench.benchmark                           # BENCHMARK.md
python -m security.harness                          # SECURITY.md (17/17)
python -m api.make_samples                          # api/samples/*.json
```

Environment used: Python 3.11.6, numpy 2.2.6, scipy 1.14.1. All RNG seeded.

## The boundary (Proof Before Power)

SENSE -> CORRELATE -> TRACK -> EVALUATE COHERENCE -> PRODUCE EVIDENCE -> HAND
OFF. CIF-LAAD stops at the C2 handoff. It never authorizes and never executes.
There is no offensive or counter-UAS capability in this codebase, by design. It
may optionally publish a track + evidence head to an external ExecutionProof
authorization layer as read-only evidence; that handoff is a documented stub.

## What to do next (do not skip the gate)

Build coherence-gated inheritance, re-measure clutter, add MOTA/MOTP/OSPA, then
run on ONE recorded dataset. No radar purchase and no customer pitch until that
Stage 0 result exists. If clutter is not bounded, escalate the kill decision.
