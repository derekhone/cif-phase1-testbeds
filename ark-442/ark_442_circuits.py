"""
ARK-442 — Circuit definitions (8 arms)
Authorization Boundary Degradation Under Verification-to-Execution Delay
Remnant Fieldworks Inc. — Derek Hone

Each arm is a two-qubit dynamic circuit on IBM Heron (basis gates: cz, id, rz, sx, x).
  - Virtual qubit 0 = Q_A (authorization qubit)
  - Virtual qubit 1 = Q_P (payload qubit)
These map to the ARK-442 rule-selected physical qubits on ibm_marrakesh
(loaded from selected_qubits.json) via initial_layout at transpile time.

Mechanism under test (verify-then-execute boundary with delay):
    prepare Q_A ;  measure(Q_A) -> classical register 'ca'
    if ca == 1:  apply X to Q_P            (payload executes only if auth reads 1)
    delay(d) on the pair                    (verification-to-execution separation)
    measure(Q_P) -> classical register 'cp' (PRIMARY readout)

The delay is realised as explicit `delay` instructions (NO dynamical decoupling,
Field 13) so that the payload/authorization idle for the nominal duration and
decoherence (T1/T2) accrues during the verify-to-execute separation. This is the
same stale-auth delay construction used in ARK-441 Arm 5 / ARK-446 Arm 5,
extended here into a delay-resolved characterization (0 / 0.5 / 1.0 / 2.0 µs).

The PRIMARY endpoint is read from the 'cp' register: P(Q_P = 1). Named classical
registers let SamplerV2 expose per-register counts (pub_result.data.cp.get_counts()),
so payload readout is unambiguous even when a mid-circuit auth measurement is present.

Arms (Field 8)
--------------
1  arm1_allow_immediate      Q_A=|1>, feedforward ON, 0.0 us delay  -> S_A_0     (ALLOW reference)
2  arm2_allow_short_delay    Q_A=|1>, feedforward ON, 0.5 us delay  -> S_A_short
3  arm3_allow_medium_delay   Q_A=|1>, feedforward ON, 1.0 us delay  -> S_A_medium
4  arm4_allow_long_delay     Q_A=|1>, feedforward ON, 2.0 us delay  -> S_A_long
5  arm5_expired_auth_deny    Q_A=|1> measured, result DISCARDED, feedforward OFF -> L_expired (PRIMARY)
6  arm6_replayed_after_expiry Q_A=|0> measured (ca=0), X replayed post-measure, cond on original ca -> L_replayed (PRIMARY)
7  arm7_reverified_after_expiry Q_A=|1> fresh reverification, feedforward ON -> S_reverified
8  arm8_idle_spam            Q_A=Q_P=|0>, no ops -> SPAM_baseline (idle readout)
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# Delay points in nanoseconds (Field 8): 0 / 0.5 / 1.0 / 2.0 microseconds.
DELAY_IMMEDIATE_NS = 0
DELAY_SHORT_NS = 500
DELAY_MEDIUM_NS = 1000
DELAY_LONG_NS = 2000

# ARK-442 rule-selected physical qubit pair on ibm_marrakesh (Heron r2),
# frozen in selected_qubits.json (Field 10 selection: RE<2%, connected, min-sum).
import os as _os, json as _json
_SEL = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "selected_qubits.json")
with open(_SEL) as _f:
    _sel = _json.load(_f)
PHYSICAL_QA = _sel["Q_A"]
PHYSICAL_QP = _sel["Q_P"]
INITIAL_LAYOUT = [PHYSICAL_QA, PHYSICAL_QP]

ARM_NAMES = [
    "arm1_allow_immediate",
    "arm2_allow_short_delay",
    "arm3_allow_medium_delay",
    "arm4_allow_long_delay",
    "arm5_expired_auth_deny",
    "arm6_replayed_after_expiry",
    "arm7_reverified_after_expiry",
    "arm8_idle_spam",
]

# Delay point (ns) associated with each ALLOW arm, for the S_A(delay) decay curve.
ARM_DELAY_NS = {
    "arm1_allow_immediate": DELAY_IMMEDIATE_NS,
    "arm2_allow_short_delay": DELAY_SHORT_NS,
    "arm3_allow_medium_delay": DELAY_MEDIUM_NS,
    "arm4_allow_long_delay": DELAY_LONG_NS,
}


def _allow_with_delay(delay_ns, name):
    """ALLOW arm: Q_A=|1>, feedforward ON, then `delay_ns` idle on the pair before
    payload readout. Models verify-then-execute with a verification-to-execution
    separation; S_A = P(Q_P=1) decays with delay via T1/T2 (H2a, descriptive)."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name=name)
    qc.x(q[0])                       # prepare Q_A = |1> (authorized)
    qc.measure(q[0], ca[0])          # authorization measurement
    with qc.if_test((ca, 1)):        # feedforward: execute payload iff auth reads 1
        qc.x(q[1])
    if delay_ns > 0:
        qc.barrier(q)
        qc.delay(delay_ns, q[0], unit="ns")
        qc.delay(delay_ns, q[1], unit="ns")
        qc.barrier(q)
    qc.measure(q[1], cp[0])
    return qc


def arm1_allow_immediate():
    return _allow_with_delay(DELAY_IMMEDIATE_NS, "arm1_allow_immediate")


def arm2_allow_short_delay():
    return _allow_with_delay(DELAY_SHORT_NS, "arm2_allow_short_delay")


def arm3_allow_medium_delay():
    return _allow_with_delay(DELAY_MEDIUM_NS, "arm3_allow_medium_delay")


def arm4_allow_long_delay():
    return _allow_with_delay(DELAY_LONG_NS, "arm4_allow_long_delay")


def arm5_expired_auth_deny():
    """Arm 5 — Q_A=|1> measured but the authorization is EXPIRED: the result is
    discarded and feedforward is OFF (no conditional on Q_P). An expired
    authorization must not execute the payload. Expect Q_P=0.
    Endpoint: L_expired = P(Q_P=1). PRIMARY."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name="arm5_expired_auth_deny")
    qc.x(q[0])                       # prepare Q_A = |1>
    qc.measure(q[0], ca[0])          # auth measured, but treated as EXPIRED (discarded)
    # feedforward OFF: no if_test, payload not executed. ca is intentionally unused.
    qc.id(q[1])                      # explicit idle on payload
    qc.measure(q[1], cp[0])
    return qc


def arm6_replayed_after_expiry():
    """Arm 6 — Q_A=|0> measured (ca=0), then X applied to Q_A AFTER the measurement
    window (an attempt to replay a stale ca=1 by flipping the auth qubit); feedforward
    stays bound to the ORIGINAL measurement ca. Replaying a stale bit post-measurement
    must not retroactively authorize. Expect Q_P=0.
    Endpoint: L_replayed = P(Q_P=1). PRIMARY."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name="arm6_replayed_after_expiry")
    # Q_A in |0> (authorization already expired / denied)
    qc.measure(q[0], ca[0])          # capture original authorization = 0
    qc.x(q[0])                       # replay attempt: flip auth qubit to |1> post-measure
    with qc.if_test((ca, 1)):        # decision remains bound to the original measurement
        qc.x(q[1])
    qc.measure(q[1], cp[0])
    return qc


def arm7_reverified_after_expiry():
    """Arm 7 — fresh reverification after expiry: Q_A is re-prepared |1> and measured
    fresh, feedforward ON on the fresh result. A fresh reverification must restore
    ALLOW. Expect Q_P=1.
    Endpoint: S_reverified = P(Q_P=1)."""
    q = QuantumRegister(2, "q")
    ca = ClassicalRegister(1, "ca")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, ca, cp, name="arm7_reverified_after_expiry")
    qc.x(q[0])                       # fresh reverification: re-prepare Q_A = |1>
    qc.measure(q[0], ca[0])          # fresh authorization measurement
    with qc.if_test((ca, 1)):        # feedforward ON on the FRESH result
        qc.x(q[1])
    qc.measure(q[1], cp[0])
    return qc


def arm8_idle_spam():
    """Arm 8 — idle; Q_A=Q_P=|0>, no ops. Idle SPAM baseline = P(Q_P=1 | prepared |0>)."""
    q = QuantumRegister(2, "q")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, cp, name="arm8_idle_spam")
    qc.id(q[1])                      # explicit idle identity on payload
    qc.measure(q[1], cp[0])
    return qc


def build_all_arms():
    """Return the 8 principal arms in preregistered order as an ordered dict."""
    builders = [
        arm1_allow_immediate,
        arm2_allow_short_delay,
        arm3_allow_medium_delay,
        arm4_allow_long_delay,
        arm5_expired_auth_deny,
        arm6_replayed_after_expiry,
        arm7_reverified_after_expiry,
        arm8_idle_spam,
    ]
    return {name: b() for name, b in zip(ARM_NAMES, builders)}


if __name__ == "__main__":
    arms = build_all_arms()
    for name, qc in arms.items():
        print(f"{name}: {qc.num_qubits} qubits, {qc.num_clbits} clbits, depth {qc.depth()} "
              f"delay_ns={ARM_DELAY_NS.get(name, '-')}")
