# CIF-LAAD: Coherent Inheritance Framework for Low-Altitude Air Domain Awareness

**Public research packet (characterization record).** Remnant Fieldworks Inc.

CIF-LAAD is a sensor-agnostic software fusion, tracking, and evidence layer. This
repository is the public *research record*: research questions, methods at a
reproducible-but-not-operational level, aggregate results, external-comparator
benchmarks, preserved failures, limitations, and integrity manifests. The runnable
implementation is not in this repository (see "Controlled access" below).

**Status:** Reviewed and approved for public release as part of the CIF-LAAD
characterization package, September 2, 2026.

**Maturity:** Simulation only. TRL 3. No hardware, no real-sensor data, no fielded
deployment. Numbers do not transfer to a real RF/EO/IR environment without further
work.

## What is in this packet

### `results/`
Aggregate, non-operational results documents (Markdown):

- `RESULTS.md` master EXP-1 through EXP-8 aggregate results.
- `EXP1_RESULTS.md` frontier summary.
- `EXP9_BENCHMARK_RESULTS.md` head-to-head vs the DSTL Stone Soup GNN tracker,
  with methodology addendum and a dated erratum.
- `EXP10_RMSE_DIAGNOSIS.md` structural RMSE root-cause diagnosis.
- `EXP11_RESULTS.md` narrow low-q remediation (adopt-with-documented-cost) and
  the rejected v2 fold filter.
- `EXP12_RESULTS.md` adaptive process-noise controller, rejected against
  pre-registered kill criteria.
- `EXP14_RESULTS.md` second external comparator (Stone Soup JPDA).
- `EXP15_RESULTS.md` scaling study and measurement-cleanliness correction.

### `integrity/`
- `FREEZE_MANIFEST.txt` per-file SHA-256 and the combined engine fingerprint
  (14 files, `8712f113...7ad45`). Allows a holder of the controlled implementation to verify that the implementation corresponds to the published frozen-engine fingerprint.
- `EXPECTED_OUTPUTS.sha256` SHA-256 of every result JSON, so a holder of the
  controlled code can verify bit-for-bit reproduction.
- `REPRODUCE.md` claim-limits, what-is-frozen, and integrity-check procedure.
  The invocation commands reference scripts that live in the controlled
  implementation repository and are not shipped here.

### `governance/`
- `CIF_LAAD_public_claims_and_publication_doctrine_PUBLIC.md` the earned-envelope
  public claims, the two-layer publication model, the controlled-access statement,
  and the access-request policy.

## What we claim, and what we do not

Every claim is bounded by what the record supports. Validated strengths
(sensor-dropout continuity, false-track suppression, compute tractability) are
reported together with their costs (positional RMSE is not a CIF-LAAD strength;
accuracy degrades with load). Rejected candidates and falsified modes are
preserved in the record, unsoftened. See the governance document for the full
tagged claim set and the verbatim framing guardrails.

## Scope boundary

CIF-LAAD performs evidence fusion and track characterization and stops at evidence
handoff. It does not perform targeting, engagement, jamming, spoofing, weapons
authorization, or autonomous counter-UAS action, and it does not authorize or
execute any such action. This is a design-scope statement, verifiable from the
architecture.

## Controlled access

The runnable implementation is access-controlled while Remnant Fieldworks evaluates
security, dual-use, and applicable export-control obligations. This does not state
or imply that CIF-LAAD has been determined to be ITAR-controlled, EAR-controlled,
or subject to any specific export-control classification; it states only that
access is controlled pending Remnant's own review.

Requests for implementation access from named university researchers, government
evaluators, and prospective research or defense partners are considered
individually. A request should state identity and affiliation, intended use, and
citizenship or entity nationality sufficient to assess export-control screening
needs. Access to a defense contractor, foreign person or entity, or overseas
researcher is gated on screening by qualified export-control counsel of exactly
what would be shared.

To request access, contact Remnant Fieldworks Inc. through the CIF-LAAD project
page. Access is granted per-approval, scoped to what the reviewer needs, and
logged.

## Citation

Research record archived on Zenodo under concept DOI
[10.5281/zenodo.22242728](https://doi.org/10.5281/zenodo.22242728). This
characterization package is version DOI
[10.5281/zenodo.22262862](https://doi.org/10.5281/zenodo.22262862). Please cite
the versioned DOI when referring to this specific record.

## License and reuse

The research record (documents, results, manifests) is published under CC BY 4.0
for scientific transparency and citation. This license applies only to the publicly
deposited research materials and does not license or grant any rights to the
controlled implementation, source code, APIs, or other non-public technical
materials. The implementation is not licensed for use here because it is not
included here. Contact Remnant Fieldworks for implementation access terms.
