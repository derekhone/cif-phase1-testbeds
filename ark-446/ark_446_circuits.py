"""
ARK-446 — Circuit definitions (8 arms) — cross-device replication on ibm_marrakesh
Remnant Fieldworks Inc. — Derek Hone

SPAM-Resolved Authorization Boundary Characterization.

Each arm is a two-qubit dynamic circuit on IBM Heron (basis gates: cz, id, rz, sx, x).
  - Virtual qubit 0 = Q_A (authorization qubit)
  - Virtual qubit 1 = Q_P (payload qubit)
These map to the ARK-446 rule-selected physical qubits on ibm_marrakesh
(loaded from selected_qubits.json) via initial_layout at transpile time.

Mechanism under test (verify-then-execute boundary):
    measure(Q_A) -> classical register 'ca'
    if ca == 1:  apply X to Q_P     (payload executes only if authorization reads 1)
    measure(Q_P) -> classical register 'cp'

The PRIMARY endpoint is read from the 'cp' register: P(Q_P = 1).
Using named classical registers lets SamplerV2 expose per-register counts
(pub_result.data.cp.get_counts()), so payload readout is unambiguous even
when a mid-circuit auth measurement is also present.

Arms
----
1  Q_A=|1> (ALLOW),  feedforward ON            -> ALLOW fidelity S_A
2  Q_A=|0> (DENY),   feedforward ON            -> DENY leakage L_D (PRIMARY)
3  Q_A unmeasured,   X unconditional on Q_P    -> ungated ALLOW control (L_control)
4  Q_A unmeasured,   no X                      -> idle SPAM baseline
5  Q_A=|1>,          feedforward ON + ~1us delay-> stale-auth analogue
6  Q_A=|0> measured, then X on Q_A, cond. on original ca -> replayed-auth analogue
7  Q_A=|+> (H),      feedforward ON            -> superposition auth
8  Q_P=|1> measured directly (no feedforward)  -> in-situ payload readout reference
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# ~1 microsecond stale-auth delay, expressed in nanoseconds
STALE_DELAY_NS = 1000

# ARK-446 rule-selected physical qubit pair on ibm_marrakesh (Heron r2),
# frozen in selected_qubits.json (Field 10 selection: RE<2%, connected, min-sum).
import os as _os, json as _json
_SEL = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "selected_qubits.json")
with open(_SEL) as _f:
    _sel = _json.load(_f)
PHYSICAL_QA = _sel["Q_A"]
PHYSICAL_QP = _sel["Q_P"]
INITIAL_LAYOUT = [PHYSICAL_QA, PHYSICAL_QP]

ARM_NAMES = [
    "arm1_allow",
    "arm2_deny",
    "arm3_ungated_control",
    "arm4_idle_spam",
    "arm5_stale_auth",
    "arm6_replayed_auth",
    "arm7_superposition_auth",
    "arm8_payload_readout_ref",
]


def _base():
    """Two-qubit register scaffold. qA=q[0], qP=q[1]. cp holds payload readout."""
    q = QuantumRegister(2, "q")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, cp)
    return qc, q, cp


def arm1_allow():
    """Arm 1 — Q_A=|1> (ALLOW), feedforward ON. Expect Q_P=1 => ALLOW fidelity S_A."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name="arm1_allow")
    qc.x(q[0])                       # prepare Q_A = |1>
    qc.measure(q[0], ca[0])          # mid-circuit authorization measurement
    with qc.if_test((ca, 1)):        # feedforward: execute payload iff auth reads 1
        qc.x(q[1])
    qc.measure(q[1], cp[0])
    return qc


def arm2_deny():
    """Arm 2 — Q_A=|0> (DENY), feedforward ON. Expect Q_P=0. PRIMARY: DENY leakage L_D."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name="arm2_deny")
    # Q_A left in |0> (DENY)
    qc.measure(q[0], ca[0])
    with qc.if_test((ca, 1)):
        qc.x(q[1])
    qc.measure(q[1], cp[0])
    return qc


def arm3_ungated_control():
    """Arm 3 — no auth gating; X applied unconditionally. Ungated ALLOW control L_control."""
    qc, q, cp = _base()
    qc.name = "arm3_ungated_control"
    qc.x(q[1])                       # payload fires with no authorization check
    qc.measure(q[1], cp[0])
    return qc


def arm4_idle_spam():
    """Arm 4 — idle; no auth, no X. Idle SPAM baseline = P(Q_P=1 | prepared |0>)."""
    qc, q, cp = _base()
    qc.name = "arm4_idle_spam"
    qc.id(q[1])                      # explicit idle identity on payload
    qc.measure(q[1], cp[0])
    return qc


def arm5_stale_auth():
    """Arm 5 — Q_A=|1>, feedforward ON, then ~1us delay before payload readout.
    Stale-auth analogue: authorization granted, execution delayed."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name="arm5_stale_auth")
    qc.x(q[0])
    qc.measure(q[0], ca[0])
    with qc.if_test((ca, 1)):
        qc.x(q[1])
    qc.delay(STALE_DELAY_NS, q[1], unit="ns")
    qc.measure(q[1], cp[0])
    return qc


def arm6_replayed_auth():
    """Arm 6 — Q_A=|0> measured (ca=0 expected), then X applied to Q_A AFTER the
    measurement window; feedforward conditioned on the ORIGINAL measurement ca.
    Replayed-auth analogue: flipping the auth qubit post-measurement must not
    retroactively authorize. Expect Q_P=0."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name="arm6_replayed_auth")
    # Q_A in |0> (DENY)
    qc.measure(q[0], ca[0])          # capture original authorization = 0
    qc.x(q[0])                       # replay: flip auth qubit to |1> AFTER measurement
    with qc.if_test((ca, 1)):        # decision still bound to original measurement
        qc.x(q[1])
    qc.measure(q[1], cp[0])
    return qc


def arm7_superposition_auth():
    """Arm 7 — Q_A=|+> (H), feedforward ON. Superposition authorization.
    Expect ~50% Q_P=1 (measurement collapses auth to 0/1 with equal probability)."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name="arm7_superposition_auth")
    qc.h(q[0])                       # prepare Q_A = |+>
    qc.measure(q[0], ca[0])
    with qc.if_test((ca, 1)):
        qc.x(q[1])
    qc.measure(q[1], cp[0])
    return qc


def arm8_payload_readout_ref():
    """Arm 8 — Q_P prepared |1> and measured directly (no feedforward).
    In-situ payload readout reference within the principal job."""
    qc, q, cp = _base()
    qc.name = "arm8_payload_readout_ref"
    qc.x(q[1])
    qc.measure(q[1], cp[0])
    return qc


def build_all_arms():
    """Return the 8 principal arms in preregistered order as an ordered dict."""
    builders = [
        arm1_allow,
        arm2_deny,
        arm3_ungated_control,
        arm4_idle_spam,
        arm5_stale_auth,
        arm6_replayed_auth,
        arm7_superposition_auth,
        arm8_payload_readout_ref,
    ]
    return {name: b() for name, b in zip(ARM_NAMES, builders)}


if __name__ == "__main__":
    arms = build_all_arms()
    for name, qc in arms.items():
        print(f"{name}: {qc.num_qubits} qubits, {qc.num_clbits} clbits, depth {qc.depth()}")
