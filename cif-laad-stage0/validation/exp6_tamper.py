"""EXP-6 Evidence / provenance tamper challenge.

Build real per-track hash-linked evidence chains from a benign run, then apply
four tamper operations to COPIES of a chain and show verify() flips True->False.

HONEST LABEL: tamper-EVIDENT, not tamper-proof. A fully trusted writer can
forge a fresh internally-consistent chain; this detects mutation of a persisted
or transmitted log.
"""
from __future__ import annotations
import copy, json, sys, time
import numpy as np
from ciflaad.fusion import FusionEngine, FusionConfig
from experiments.laad_series import scenarios_ext as sx


def _longest_chain(eng):
    best = None
    for tr in eng.all_tracks():
        if best is None or len(tr.evidence_chain) > len(best):
            best = tr.evidence_chain
    return best


def main():
    t0 = time.time()
    scen, _ = sx.benign(100)
    eng = FusionEngine(FusionConfig())
    for t, truth, obs in scen.frames():
        eng.process(obs, t)

    chain = _longest_chain(eng)
    pristine_ok = chain.verify()
    n = len(chain)
    k = max(1, n // 2)
    results = {"chain_length": n, "pristine_verify": pristine_ok, "tampers": {}}

    # (a) mutate a payload field
    c = copy.deepcopy(chain)
    recs = c._records
    recs[k].payload = dict(recs[k].payload); recs[k].payload["_injected"] = "tampered"
    results["tampers"]["mutate_payload"] = {"verify_after": c.verify(), "detected": not c.verify()}

    # (b) reorder two records
    c = copy.deepcopy(chain)
    c._records[k], c._records[k + 1] = c._records[k + 1], c._records[k]
    results["tampers"]["reorder_records"] = {"verify_after": c.verify(), "detected": not c.verify()}

    # (c) delete a record
    c = copy.deepcopy(chain)
    del c._records[k]
    results["tampers"]["delete_record"] = {"verify_after": c.verify(), "detected": not c.verify()}

    # (d) substitute a record (re-hash it locally but not the downstream links)
    c = copy.deepcopy(chain)
    victim = c._records[k]
    forged_payload = dict(victim.payload); forged_payload["substituted"] = True
    from ciflaad.evidence import _hash
    victim.payload = forged_payload
    victim.hash = _hash(victim.prev_hash, victim.seq, victim.timestamp,
                        victim.event_type, forged_payload)
    results["tampers"]["substitute_record"] = {"verify_after": c.verify(), "detected": not c.verify()}

    results["all_tampers_detected"] = all(v["detected"] for v in results["tampers"].values())
    results["engine_verify_all"] = eng.verify_all_evidence()

    out = {"meta": {"experiment": "EXP-6 evidence tamper challenge",
                    "numpy": np.__version__, "python": sys.version.split()[0],
                    "label": "tamper-EVIDENT, not tamper-proof",
                    "wallclock_s": round(time.time() - t0, 2)},
           "results": results}
    with open("experiments/laad_series/out/exp6_tamper.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("wrote exp6_tamper.json  all_tampers_detected =", results["all_tampers_detected"],
          " pristine_ok =", pristine_ok)


if __name__ == "__main__":
    main()
