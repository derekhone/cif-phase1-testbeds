"""
ARK-444 — Circuit definitions (8 arms)  [v1.1 — flattened control flow]
Decision-to-Execution Integrity
Remnant Fieldworks Inc. — Derek Hone

Each arm is a two-qubit dynamic circuit on IBM Heron (basis gates: cz, id, rz, sx, x).
  - Virtual qubit 0 = Q_A (approval / integrity-commitment qubit, reused for execution verify)
  - Virtual qubit 1 = Q_P (payload qubit)
These map to the ARK-444 rule-selected physical qubits on ibm_marrakesh
(loaded from selected_qubits.json) via initial_layout at transpile time.

CONTROL-FLOW AMENDMENT (v1.1, documented in the preregistration amendment):
The v1.0 integrity gate used a NESTED if_test ( if ca==1: if ce==1: X ). IBM Qiskit
Runtime does NOT support nested conditionals (job d9cmdvsjeosc73fgfk5g errored with
code 1524 before producing ANY counts). The gate is flattened to a SINGLE if_test on a
single 2-bit integrity register `ci` with the combined value 0b11 == 3, which is exactly
the supported single-register feedforward pattern proven in ARK-442. Mid-circuit `reset`
at top level (never inside a conditional) IS supported and is retained. The measurable
semantics are UNCHANGED: payload fires iff approval AND fresh execution-verify are both 1.
Because the v1.0 job produced zero data, this amendment introduces no outcome-dependent
bias (no "rescue after failure" — there was no result to rescue).

Mechanism under test — a tamper-evident decision-to-execution binding:
    Approval phase:   prepare Q_A per APPROVED action ; measure(Q_A) -> ci[0]  (approval)
    Execution phase:  reset(Q_A) ; prepare Q_A per EXECUTED action ; measure(Q_A) -> ci[1] (verify)
    Integrity gate:   if (ci == 0b11):  X(Q_P)          # approval AND execution-verify both 1
    Payload readout:  measure(Q_P) -> cp   (PRIMARY endpoint)

The payload is bound to the FRESH execution-time verification ci[1], NOT to the stale
approval ci[0] alone. For an unchanged approved action both bits are 1 and the payload
fires. Any post-approval alteration drives the execution-verify bit to 0, so the integrity
gate withholds the payload (FAIL CLOSED). A replayed stale approval provides neither a set
approval bit nor a fresh matching verification, so it also fails closed. A mutated action
that is RE-VERIFIED re-establishes both bits and correctly executes.

The single committed bit is a HARDWARE ABSTRACTION of an action signature. This is a
metrological characterization of a tamper-evident binding on this hardware, NOT a
cryptographic integrity guarantee. The payload readout uses its own classical register
(cp) so SamplerV2 exposes it unambiguously even with mid-circuit measurements.

Arms (Field 8)
--------------
1  arm1_approved_unchanged      ci=11 (match)               -> fires   -> S_match      (reference)
2  arm2_destination_changed     ci=01 (verify != bound)     -> withheld -> L_dest      (PRIMARY)
3  arm3_amount_changed          ci=01 (param !=)            -> withheld -> L_amount    (PRIMARY)
4  arm4_operation_changed       ci=01 (op type !=)          -> withheld -> L_optype    (PRIMARY)
5  arm5_extra_action_appended   ci=01 (appended X -> 0)     -> withheld -> L_append    (PRIMARY)
6  arm6_approval_replayed       ci=00 (replay flip)         -> withheld -> L_replay    (PRIMARY)
7  arm7_mutated_then_reverified ci=11 (fresh re-verify)     -> fires   -> S_reverified (recovery)
8  arm8_idle_spam               idle payload readout        -> none    -> SPAM_baseline
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# ARK-444 rule-selected physical qubit pair on ibm_marrakesh (Heron r2),
# frozen in selected_qubits.json (Field 10 selection: RE<2%, connected, min-sum).
import os as _os, json as _json
_SEL = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "selected_qubits.json")
with open(_SEL) as _f:
    _sel = _json.load(_f)
PHYSICAL_QA = _sel["Q_A"]
PHYSICAL_QP = _sel["Q_P"]
INITIAL_LAYOUT = [PHYSICAL_QA, PHYSICAL_QP]

ARM_NAMES = [
    "arm1_approved_unchanged",
    "arm2_destination_changed",
    "arm3_amount_changed",
    "arm4_operation_changed",
    "arm5_extra_action_appended",
    "arm6_approval_replayed",
    "arm7_mutated_then_reverified",
    "arm8_idle_spam",
]

# Alteration class label per arm (for reporting; descriptive only).
ARM_CLASS = {
    "arm1_approved_unchanged": "match_reference",
    "arm2_destination_changed": "alteration_destination",
    "arm3_amount_changed": "alteration_amount",
    "arm4_operation_changed": "alteration_optype",
    "arm5_extra_action_appended": "alteration_append",
    "arm6_approval_replayed": "replay",
    "arm7_mutated_then_reverified": "reverified_recovery",
    "arm8_idle_spam": "idle_spam",
}

# Integrity register bit layout (single register -> supported single-condition feedforward):
#   ci[0] = approval signature (ca)
#   ci[1] = fresh execution-time verification (ce)
# Payload fires iff ci == 0b11 (both bits set) == integer 3.
CI_FIRE = 3


def _new():
    q = QuantumRegister(2, "q")
    ci = ClassicalRegister(2, "ci")   # ci[0]=approval, ci[1]=execution-verify
    cp = ClassicalRegister(1, "cp")   # payload readout (PRIMARY)
    return q, ci, cp


def _integrity_gate(qc, q, ci):
    """Payload fires iff approval (ci[0]==1) AND execution-verify (ci[1]==1), i.e. ci==0b11.
    Single-register if_test (supported feedforward; no nested conditionals)."""
    with qc.if_test((ci, CI_FIRE)):
        qc.x(q[1])


def arm1_approved_unchanged():
    """Approved action executed unchanged: approval=1, execution re-verifies identically=1,
    integrity gate fires. Endpoint S_match = P(Q_P=1). Reference (matched)."""
    q, ci, cp = _new()
    qc = QuantumCircuit(q, ci, cp, name="arm1_approved_unchanged")
    qc.x(q[0]); qc.measure(q[0], ci[0])                    # approval signature = 1
    qc.reset(q[0]); qc.x(q[0]); qc.measure(q[0], ci[1])    # execution re-verify = 1 (matches)
    _integrity_gate(qc, q, ci)
    qc.measure(q[1], cp[0])
    return qc


def arm2_destination_changed():
    """Destination changed after approval: the executed action routes to a destination
    that was not the one bound at approval, so the execution verification against the
    committed approval does not match (verify=0). Payload withheld (fail closed).
    Endpoint L_dest = P(Q_P=1). PRIMARY."""
    q, ci, cp = _new()
    qc = QuantumCircuit(q, ci, cp, name="arm2_destination_changed")
    qc.x(q[0]); qc.measure(q[0], ci[0])                    # approval signature = 1
    qc.reset(q[0]); qc.measure(q[0], ci[1])                # changed destination: verify=0
    _integrity_gate(qc, q, ci)
    qc.measure(q[1], cp[0])
    return qc


def arm3_amount_changed():
    """Amount / parameter changed after approval: the executed action's parameter differs
    from the approved one; the execution verification does not match (verify=0). Payload
    withheld. Distinct construction (explicit idle on the commitment qubit).
    Endpoint L_amount = P(Q_P=1). PRIMARY."""
    q, ci, cp = _new()
    qc = QuantumCircuit(q, ci, cp, name="arm3_amount_changed")
    qc.x(q[0]); qc.measure(q[0], ci[0])                    # approval signature = 1
    qc.reset(q[0]); qc.id(q[0]); qc.measure(q[0], ci[1])   # changed parameter: verify=0
    _integrity_gate(qc, q, ci)
    qc.measure(q[1], cp[0])
    return qc


def arm4_operation_changed():
    """Operation type changed after approval: the executed op type differs from the
    approved op; the commitment fails to reconstruct (X.X = I leaves |0>), verify=0.
    Payload withheld. Distinct construction (op-type flip that nets to no signature).
    Endpoint L_optype = P(Q_P=1). PRIMARY."""
    q, ci, cp = _new()
    qc = QuantumCircuit(q, ci, cp, name="arm4_operation_changed")
    qc.x(q[0]); qc.measure(q[0], ci[0])                    # approval signature = 1
    qc.reset(q[0]); qc.x(q[0]); qc.x(q[0]); qc.measure(q[0], ci[1])  # changed op: X.X=I -> 0
    _integrity_gate(qc, q, ci)
    qc.measure(q[1], cp[0])
    return qc


def arm5_extra_action_appended():
    """Extra action appended after verification: the execution first reconstructs the
    approved signature (X -> |1>), but an EXTRA unapproved action is appended before the
    integrity re-measurement (a second X -> |0>). The re-measurement catches the tamper
    (verify=0), so the payload is withheld (fail closed). The appended action was never
    approved and must not execute. Endpoint L_append = P(Q_P=1). PRIMARY."""
    q, ci, cp = _new()
    qc = QuantumCircuit(q, ci, cp, name="arm5_extra_action_appended")
    qc.x(q[0]); qc.measure(q[0], ci[0])                    # approval signature = 1
    qc.reset(q[0])
    qc.x(q[0])                                             # execution reconstructs approved |1>
    qc.barrier(q)
    qc.x(q[0])                                             # EXTRA appended (unapproved) action -> |0>
    qc.measure(q[0], ci[1])                                # integrity re-check catches tamper -> 0
    _integrity_gate(qc, q, ci)
    qc.measure(q[1], cp[0])
    return qc


def arm6_approval_replayed():
    """Original approval replayed: no fresh approval is captured at execution (approval=0);
    an attacker REPLAYS the stale approval by flipping the commitment qubit AFTER the
    approval-measurement window. The decision remains bound to the original measurement
    (approval bit = 0) and the fresh execution verification is absent (verify=0), so the
    replayed token does not authorize. Payload withheld. Mirrors ARK-442 Arm 6 (post-measure
    replay). Endpoint L_replay = P(Q_P=1). PRIMARY."""
    q, ci, cp = _new()
    qc = QuantumCircuit(q, ci, cp, name="arm6_approval_replayed")
    qc.measure(q[0], ci[0])                                # capture original approval = 0 (|0>)
    qc.x(q[0])                                             # REPLAY attempt: flip post-measure
    qc.reset(q[0]); qc.measure(q[0], ci[1])                # fresh execution verify = 0 (none)
    _integrity_gate(qc, q, ci)                             # approval bit=0 -> withheld
    qc.measure(q[1], cp[0])
    return qc


def arm7_mutated_then_reverified():
    """Mutated payload re-verified before execution: after alteration, the (new) action
    is RE-APPROVED fresh (approval=1) and the execution verification matches the re-approval
    (verify=1). Because what executes is now exactly what was (re)verified, the integrity gate
    fires. Endpoint S_reverified = P(Q_P=1). Recovery arm."""
    q, ci, cp = _new()
    qc = QuantumCircuit(q, ci, cp, name="arm7_mutated_then_reverified")
    qc.x(q[0]); qc.measure(q[0], ci[0])                    # fresh re-approval of mutated action = 1
    qc.reset(q[0]); qc.x(q[0]); qc.measure(q[0], ci[1])    # execution verify matches re-approval = 1
    _integrity_gate(qc, q, ci)
    qc.measure(q[1], cp[0])
    return qc


def arm8_idle_spam():
    """Idle SPAM baseline: Q_P=|0>, no ops. SPAM_baseline = P(Q_P=1 | prepared |0>)."""
    q = QuantumRegister(2, "q")
    cp = ClassicalRegister(1, "cp")
    qc = QuantumCircuit(q, cp, name="arm8_idle_spam")
    qc.id(q[1])
    qc.measure(q[1], cp[0])
    return qc


def build_all_arms():
    """Return the 8 principal arms in preregistered order as an ordered dict."""
    builders = [
        arm1_approved_unchanged,
        arm2_destination_changed,
        arm3_amount_changed,
        arm4_operation_changed,
        arm5_extra_action_appended,
        arm6_approval_replayed,
        arm7_mutated_then_reverified,
        arm8_idle_spam,
    ]
    return {name: b() for name, b in zip(ARM_NAMES, builders)}


if __name__ == "__main__":
    arms = build_all_arms()
    for name, qc in arms.items():
        print(f"{name}: {qc.num_qubits} qubits, {qc.num_clbits} clbits, depth {qc.depth()} "
              f"class={ARM_CLASS.get(name)}")
