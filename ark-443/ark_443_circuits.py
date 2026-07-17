"""
ARK-443 — Circuit definitions (8 arms)
Two-of-Three (M-of-N) Quorum Authorization
Remnant Fieldworks Inc. — Derek Hone

Each arm is a four-qubit dynamic circuit on IBM Heron (basis gates: cz, id, rz, sx, x).
  - Virtual qubit 0 = Q_P  (payload qubit; PRIMARY endpoint)
  - Virtual qubit 1 = Q_A1 (authorizer channel 1)
  - Virtual qubit 2 = Q_A2 (authorizer channel 2)
  - Virtual qubit 3 = Q_A3 (authorizer channel 3)
These map to the ARK-443 rule-selected physical qubits on ibm_marrakesh
(loaded from selected_qubits.json) via initial_layout at transpile time.

Mechanism under test — a 2-of-3 quorum (separation-of-duties) authorization boundary:
    Authorization phase:  prepare each authorizer per its vote ; measure -> ca[0..2]
    Quorum gate:          if popcount(ca) >= 2:  X(Q_P)     # classical majority
    Payload readout:      measure(Q_P) -> cp   (PRIMARY endpoint)

There are NO inter-qubit two-qubit gates. The quorum is realized purely by CLASSICAL
feedforward on the three measured authorization bits. The payload fires iff at least two
of the three measured authorization bits are 1.

CONTROL-FLOW PATTERN (learned in ARK-444):
IBM Qiskit Runtime does NOT support NESTED if_test (job errors with code 1524). It DOES
support multiple SEQUENTIAL single-register if_test blocks. The majority-of-3 predicate
"popcount(ca) >= 2" is the set of 3-bit register values {3,5,6,7} (i.e. 011,101,110,111).
The gate is therefore realized as FOUR sequential single-register if_test blocks, one per
majority value; at most one block fires on any given shot (the values are mutually
exclusive), so the net effect is a single conditional X on the payload. Because majority
is symmetric under bit permutation, this predicate is invariant to the ca bit/endianness
ordering. Mid-circuit `reset` at top level (never inside a conditional) IS supported and is
used by the replay/tamper arm.

The three committed authorization bits are a HARDWARE ABSTRACTION of independent approvals.
This is a metrological characterization of a quorum-gated execution rule on this hardware,
NOT a cryptographic guarantee (no signatures/MACs, no Byzantine-agreement claim). The
payload readout uses its own classical register (cp) so SamplerV2 exposes it unambiguously
even with mid-circuit measurements.

HONEST BOUNDARY NOTE (Field 23): a 2-of-3 quorum protects against ONE compromised or
replayed channel. TWO colluding channels form a LEGITIMATE quorum and would execute — this
is the intended design limit of M-of-N separation of duties, not a defect.

Arms (Field 8)
--------------
1  arm1_0of3_deny             ca=000 -> DENY   -> L_0of3        (baseline)  PRIMARY
2  arm2_1of3_deny             ca=100 -> DENY   -> L_1of3        (no unilateral) PRIMARY
3  arm3_2of3_allow            ca=110 -> ALLOW  -> S_2of3        (quorum)    PRIMARY
4  arm4_3of3_allow            ca=111 -> ALLOW  -> S_3of3        (unanimous)
5  arm5_1of3_altchannel_deny  ca=001 -> DENY   -> L_1of3_alt    (alt channel) PRIMARY
6  arm6_degraded_quorum_allow A1=A2=1, A3=H    -> ALLOW  -> S_degraded (tolerance)
7  arm7_replay_tamper_deny    A1 vote 0 recorded then post-vote flip -> DENY -> L_replay PRIMARY
8  arm8_idle_spam             idle payload readout            -> SPAM_baseline
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# ARK-443 rule-selected physical qubits on ibm_marrakesh (Heron r2),
# frozen in selected_qubits.json (Field 10: 4 lowest-RE, RE<2%, no connectivity).
import os as _os, json as _json
_SEL = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "selected_qubits.json")
with open(_SEL) as _f:
    _sel = _json.load(_f)
PHYSICAL_QP = _sel["Q_P"]
PHYSICAL_QA1 = _sel["Q_A1"]
PHYSICAL_QA2 = _sel["Q_A2"]
PHYSICAL_QA3 = _sel["Q_A3"]
# Virtual q[0]=Q_P, q[1]=Q_A1, q[2]=Q_A2, q[3]=Q_A3
INITIAL_LAYOUT = [PHYSICAL_QP, PHYSICAL_QA1, PHYSICAL_QA2, PHYSICAL_QA3]

ARM_NAMES = [
    "arm1_0of3_deny",
    "arm2_1of3_deny",
    "arm3_2of3_allow",
    "arm4_3of3_allow",
    "arm5_1of3_altchannel_deny",
    "arm6_degraded_quorum_allow",
    "arm7_replay_tamper_deny",
    "arm8_idle_spam",
]

# Expected authorization semantics per arm (for reporting; descriptive only).
ARM_CLASS = {
    "arm1_0of3_deny": "deny_0of3",
    "arm2_1of3_deny": "deny_1of3",
    "arm3_2of3_allow": "allow_2of3",
    "arm4_3of3_allow": "allow_3of3",
    "arm5_1of3_altchannel_deny": "deny_1of3_alt",
    "arm6_degraded_quorum_allow": "allow_degraded",
    "arm7_replay_tamper_deny": "deny_replay",
    "arm8_idle_spam": "idle_spam",
}

# Whether each arm is expected to ALLOW (payload fires) or DENY (withheld).
ARM_EXPECT = {
    "arm1_0of3_deny": "DENY",
    "arm2_1of3_deny": "DENY",
    "arm3_2of3_allow": "ALLOW",
    "arm4_3of3_allow": "ALLOW",
    "arm5_1of3_altchannel_deny": "DENY",
    "arm6_degraded_quorum_allow": "ALLOW",
    "arm7_replay_tamper_deny": "DENY",
    "arm8_idle_spam": "SPAM",
}

# Majority-of-3 predicate: 3-bit register values with popcount >= 2.
#   011=3, 101=5, 110=6, 111=7.  (Symmetric -> endianness-invariant.)
QUORUM_VALUES = [3, 5, 6, 7]


def _new():
    q = QuantumRegister(4, "q")       # q0=Q_P, q1=Q_A1, q2=Q_A2, q3=Q_A3
    ca = ClassicalRegister(3, "ca")   # ca[0..2] = authorization bits from A1,A2,A3
    cp = ClassicalRegister(1, "cp")   # payload readout (PRIMARY)
    return q, ca, cp


def _quorum_gate(qc, q, ca):
    """Payload fires iff classical majority of the 3 authorization bits is >= 2.
    Realized as 4 SEQUENTIAL single-register if_test blocks (one per majority value);
    mutually exclusive, so at most one fires per shot. No nested conditionals."""
    for v in QUORUM_VALUES:
        with qc.if_test((ca, v)):
            qc.x(q[0])


def arm1_0of3_deny():
    """No authorizer approves (ca=000). Quorum not met -> payload withheld (DENY).
    Baseline leakage: L_0of3 = P(Q_P=1). PRIMARY."""
    q, ca, cp = _new()
    qc = QuantumCircuit(q, ca, cp, name="arm1_0of3_deny")
    qc.measure(q[1], ca[0])          # A1 vote = 0
    qc.measure(q[2], ca[1])          # A2 vote = 0
    qc.measure(q[3], ca[2])          # A3 vote = 0
    _quorum_gate(qc, q, ca)
    qc.measure(q[0], cp[0])
    return qc


def arm2_1of3_deny():
    """Exactly one authorizer approves (ca=100). One channel alone must NOT authorize
    -> payload withheld (DENY). No-unilateral: L_1of3 = P(Q_P=1). PRIMARY."""
    q, ca, cp = _new()
    qc = QuantumCircuit(q, ca, cp, name="arm2_1of3_deny")
    qc.x(q[1]); qc.measure(q[1], ca[0])   # A1 vote = 1
    qc.measure(q[2], ca[1])               # A2 vote = 0
    qc.measure(q[3], ca[2])               # A3 vote = 0
    _quorum_gate(qc, q, ca)
    qc.measure(q[0], cp[0])
    return qc


def arm3_2of3_allow():
    """Two of three authorizers approve (ca=110). Quorum met -> payload fires (ALLOW).
    S_2of3 = P(Q_P=1). PRIMARY."""
    q, ca, cp = _new()
    qc = QuantumCircuit(q, ca, cp, name="arm3_2of3_allow")
    qc.x(q[1]); qc.measure(q[1], ca[0])   # A1 vote = 1
    qc.x(q[2]); qc.measure(q[2], ca[1])   # A2 vote = 1
    qc.measure(q[3], ca[2])               # A3 vote = 0
    _quorum_gate(qc, q, ca)
    qc.measure(q[0], cp[0])
    return qc


def arm4_3of3_allow():
    """All three authorizers approve (ca=111). Unanimous quorum -> payload fires (ALLOW).
    S_3of3 = P(Q_P=1)."""
    q, ca, cp = _new()
    qc = QuantumCircuit(q, ca, cp, name="arm4_3of3_allow")
    qc.x(q[1]); qc.measure(q[1], ca[0])   # A1 vote = 1
    qc.x(q[2]); qc.measure(q[2], ca[1])   # A2 vote = 1
    qc.x(q[3]); qc.measure(q[3], ca[2])   # A3 vote = 1
    _quorum_gate(qc, q, ca)
    qc.measure(q[0], cp[0])
    return qc


def arm5_1of3_altchannel_deny():
    """Exactly one authorizer approves, but via a DIFFERENT channel (ca=001). Still one
    channel alone -> payload withheld (DENY). Confirms no-unilateral is channel-agnostic.
    L_1of3_alt = P(Q_P=1). PRIMARY."""
    q, ca, cp = _new()
    qc = QuantumCircuit(q, ca, cp, name="arm5_1of3_altchannel_deny")
    qc.measure(q[1], ca[0])               # A1 vote = 0
    qc.measure(q[2], ca[1])               # A2 vote = 0
    qc.x(q[3]); qc.measure(q[3], ca[2])   # A3 vote = 1
    _quorum_gate(qc, q, ca)
    qc.measure(q[0], cp[0])
    return qc


def arm6_degraded_quorum_allow():
    """Two honest authorizers approve (A1=A2=|1>) and the third channel is DEGRADED /
    noisy (A3 prepared in superposition via H, random vote). Because two honest approvals
    already meet quorum, the payload fires REGARDLESS of the noisy third bit -> ALLOW.
    Tolerance arm: S_degraded = P(Q_P=1). (A quorum of two honest channels is robust to a
    single degraded channel.)"""
    q, ca, cp = _new()
    qc = QuantumCircuit(q, ca, cp, name="arm6_degraded_quorum_allow")
    qc.x(q[1]); qc.measure(q[1], ca[0])   # A1 vote = 1 (honest)
    qc.x(q[2]); qc.measure(q[2], ca[1])   # A2 vote = 1 (honest)
    qc.h(q[3]); qc.measure(q[3], ca[2])   # A3 degraded: random 0/1
    _quorum_gate(qc, q, ca)
    qc.measure(q[0], cp[0])
    return qc


def arm7_replay_tamper_deny():
    """Post-vote replay/tamper on one channel. A1 is prepared |0> and its vote is RECORDED
    into ca[0] (=0). AFTER the authorization measurement window, an attacker flips A1 to |1>
    (reset then X) to REPLAY an approval. The quorum gate reads the RECORDED votes (ca), not
    the post-hoc physical state, so with A2=A3=0 the recorded register is 000 -> quorum not
    met -> payload withheld (DENY). A single post-vote-tampered channel cannot authorize.
    L_replay = P(Q_P=1). PRIMARY."""
    q, ca, cp = _new()
    qc = QuantumCircuit(q, ca, cp, name="arm7_replay_tamper_deny")
    qc.measure(q[1], ca[0])               # A1 vote RECORDED = 0
    qc.measure(q[2], ca[1])               # A2 vote = 0
    qc.measure(q[3], ca[2])               # A3 vote = 0
    qc.barrier(q)
    qc.reset(q[1]); qc.x(q[1])            # POST-VOTE tamper: physically flip A1 to |1> (too late)
    _quorum_gate(qc, q, ca)               # gate reads recorded ca=000 -> DENY
    qc.measure(q[0], cp[0])
    return qc


def arm8_idle_spam():
    """Idle SPAM baseline: Q_P=|0>, no ops. SPAM_baseline = P(Q_P=1 | prepared |0>)."""
    q = QuantumRegister(4, "q")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, cp, name="arm8_idle_spam")
    qc.id(q[0])
    qc.measure(q[0], cp[0])
    return qc


def build_all_arms():
    """Return the 8 principal arms in preregistered order as an ordered dict."""
    builders = [
        arm1_0of3_deny,
        arm2_1of3_deny,
        arm3_2of3_allow,
        arm4_3of3_allow,
        arm5_1of3_altchannel_deny,
        arm6_degraded_quorum_allow,
        arm7_replay_tamper_deny,
        arm8_idle_spam,
    ]
    return {name: b() for name, b in zip(ARM_NAMES, builders)}


if __name__ == "__main__":
    arms = build_all_arms()
    for name, qc in arms.items():
        print(f"{name}: {qc.num_qubits} qubits, {qc.num_clbits} clbits, depth {qc.depth()} "
              f"expect={ARM_EXPECT.get(name)} class={ARM_CLASS.get(name)}")
