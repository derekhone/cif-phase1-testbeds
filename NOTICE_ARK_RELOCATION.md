# NOTICE — Repository Scope & ARK Track Relocation

**Date:** 2026-07-17 (UTC)

> **Naming note.** This work was originally published under the working title Unified Inheritance Physics (UIP). The active framework name is now the Coherent Inheritance Framework (CIF), and this repository is now `cif-phase1-testbeds`. Historical files, commit tags, and DOI records retain their original titles where necessary for provenance; GitHub automatically redirects the former `uip-phase1-testbeds` URLs.

## For reviewers of the Coherent Inheritance Framework (CIF) Phase 1 program (formerly UIP)

This repository (`cif-phase1-testbeds`) is the record of the **CIF Phase 1 physics falsification
program** — the A–B packet plus tests C, D–E, F, G, H, I (final ledger: 4 confirmed / 5 falsified).
That program is **closed**; its canonical archive is **DOI 10.5281/zenodo.21246246**. Nothing further
will be added to the Phase 1 physics record.

## What moved, and why

For a period, a **separate, unrelated track** — the **ARK authorization-boundary experiments**
(ARK-441, ARK-446, ARK-442, ARK-444, ARK-443) — was committed into this repository under isolated
`ark-4NN/` folders. As stated in the original `ark-441/INDEPENDENCE_NOTICE.md` (committed at that
experiment's lock time), those experiments were **never part of UIP Phase 1 or Phase 2**; they shared
this repository only as a convenience for reviewing hardware testbeds in one place.

To keep the closed Phase 1 physics record clean and unambiguous for review, that track has been
**relocated to its own dedicated repository**:

- **New home:** https://github.com/derekhone/executionproof-testbeds
- **Dataset DOI (unchanged):** 10.5281/zenodo.21398676 (ExecutionProof / ARK authorization series)

The ARK authorization folders have been removed from the tip of `main` in this repository. **The original
commit history and the release tags `ark-441-v1.0`, `ark-446-v1.0`, `ark-442-v1.0`, `ark-444-v1.0`,
`ark-443-v1.0` remain intact** in this repository for audit — this is a forward cleanup commit, **not** a
history rewrite. The preregistration integrity of each ARK experiment rests on those original timestamped
commits, which are preserved.

## Note on `ark-dm-1/`

The `ark-dm-1/` folder is a **separate preregistered physics test** (a galaxy-rotation-curve / dark-matter
model comparison inspired by the UIP/Ark library, verdict: FAIL). Per its own preregistration it is **not**
part of the UIP Phase 1 falsification program either, and it is **not** part of the ExecutionProof
authorization track. It is retained here, clearly labeled, pending its own disposition; it should not be
read or cited as a Phase 1 falsification-program result.

## Summary

| Track | Home | DOI | Status |
|-------|------|-----|--------|
| CIF Phase 1 (physics falsification, formerly UIP) | this repo (`cif-phase1-testbeds`) | 10.5281/zenodo.21246246 | Closed; under review |
| ExecutionProof / ARK authorization | `executionproof-testbeds` | 10.5281/zenodo.21398676 | Ongoing |
| ARK-DM-1 (dark-matter physics test) | this repo, `ark-dm-1/` (separate) | — | Complete (FAIL); separate |
