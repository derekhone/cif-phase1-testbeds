"""
ARK-443 — Preregistered qubit selection on ibm_marrakesh (Heron r2)
Remnant Fieldworks Inc. — Derek Hone

Selection rule (preregistered, Field 10):
  - FOUR qubits required (1 payload Q_P + 3 authorizers Q_A1,Q_A2,Q_A3).
  - Each qubit must have readout_error < 0.020 from today's calibration snapshot.
  - NO connectivity constraint (justified: quorum is realized by CLASSICAL
    feedforward; there are NO inter-qubit 2-qubit gates in any arm).
  - Deterministic: take the 4 lowest-RE qubits. Assign the single lowest-RE
    qubit -> Q_P (payload gets the best qubit). The remaining three, ordered by
    ascending physical index, -> Q_A1, Q_A2, Q_A3.

Outputs:
  - calibration_snapshot_marrakesh_20260716.json  (per-qubit readout errors + meta)
  - selected_qubits.json                           (the frozen four, RE values, layout)
"""

import json
import os
from datetime import datetime, timezone

from qiskit_ibm_runtime import QiskitRuntimeService

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = "/home/ubuntu/.config/abacusai_auth_secrets.json"

BACKEND_NAME = "ibm_marrakesh"
CHANNEL = "ibm_quantum_platform"
INSTANCE = "open-instance"
RE_CEILING = 0.020
N_SELECT = 4


def load_token():
    with open(SECRETS) as f:
        return json.load(f)["ibm quantum"]["secrets"]["api_token"]["value"]


def main():
    token = load_token()
    service = QiskitRuntimeService(channel=CHANNEL, token=token, instance=INSTANCE)
    backend = service.backend(BACKEND_NAME)
    props = backend.properties()
    n = backend.num_qubits

    readout_error = {}
    for q in range(n):
        try:
            readout_error[q] = float(props.readout_error(q))
        except Exception:
            readout_error[q] = None

    # Qualifying = RE strictly below ceiling.
    qualifying = [
        {"qubit": q, "re": re}
        for q, re in readout_error.items()
        if re is not None and re < RE_CEILING
    ]
    if len(qualifying) < N_SELECT:
        raise SystemExit(
            f"[SELECT] Only {len(qualifying)} qubits with RE < {RE_CEILING}; "
            f"need {N_SELECT}. Cannot proceed."
        )

    # Deterministic tie-break: sort by (RE asc, physical index asc).
    qualifying.sort(key=lambda d: (d["re"], d["qubit"]))
    chosen = qualifying[:N_SELECT]

    # Payload gets the single lowest-RE qubit.
    q_p_entry = chosen[0]
    q_p = q_p_entry["qubit"]
    # The remaining three authorizers ordered by ascending physical index.
    authorizers = sorted((c["qubit"] for c in chosen[1:]))
    q_a1, q_a2, q_a3 = authorizers

    re_qp = readout_error[q_p]
    re_a1 = readout_error[q_a1]
    re_a2 = readout_error[q_a2]
    re_a3 = readout_error[q_a3]

    snapshot = {
        "experiment_id": "ARK-443",
        "backend": BACKEND_NAME,
        "instance": INSTANCE,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "num_qubits": n,
        "re_ceiling": RE_CEILING,
        "readout_error": {str(k): v for k, v in readout_error.items()},
        "backend_version": getattr(backend, "version", None),
        "processor_type": str(getattr(backend, "processor_type", None)),
    }
    snap_path = os.path.join(HERE, "calibration_snapshot_marrakesh_20260716.json")
    with open(snap_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    # initial_layout maps virtual register q[0..3] -> physical:
    #   q[0]=Q_P, q[1]=Q_A1, q[2]=Q_A2, q[3]=Q_A3
    initial_layout = [q_p, q_a1, q_a2, q_a3]

    selection = {
        "experiment_id": "ARK-443",
        "backend": BACKEND_NAME,
        "selection_rule": (
            "4 lowest-RE qubits with RE < 0.020, NO connectivity constraint "
            "(classical feedforward, no 2q gates); lowest-RE -> Q_P; remaining "
            "three by ascending physical index -> Q_A1,Q_A2,Q_A3"
        ),
        "Q_P": q_p,
        "Q_A1": q_a1,
        "Q_A2": q_a2,
        "Q_A3": q_a3,
        "readout_error_Q_P": re_qp,
        "readout_error_Q_A1": re_a1,
        "readout_error_Q_A2": re_a2,
        "readout_error_Q_A3": re_a3,
        "max_readout_error": max(re_qp, re_a1, re_a2, re_a3),
        "initial_layout": initial_layout,
        "num_qualifying_qubits": len(qualifying),
        "top8_qualifying": qualifying[:8],
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
    }
    sel_path = os.path.join(HERE, "selected_qubits.json")
    with open(sel_path, "w") as f:
        json.dump(selection, f, indent=2)

    print(f"[SELECT] backend={BACKEND_NAME} qubits={n} qualifying={len(qualifying)}")
    print(f"[SELECT] Q_P={q_p} (RE={re_qp:.4%})  "
          f"Q_A1={q_a1} (RE={re_a1:.4%})  "
          f"Q_A2={q_a2} (RE={re_a2:.4%})  "
          f"Q_A3={q_a3} (RE={re_a3:.4%})")
    print(f"[SELECT] initial_layout={initial_layout}  "
          f"max_RE={max(re_qp, re_a1, re_a2, re_a3):.4%}")
    print(f"[SELECT] wrote {snap_path}")
    print(f"[SELECT] wrote {sel_path}")


if __name__ == "__main__":
    main()
