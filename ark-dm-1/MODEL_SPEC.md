# ARK-DM-1 Model Specification

## Purpose

This file defines the planned model comparison for ARK-DM-1 before code execution.

The purpose is to make the comparison clear, reproducible, and resistant to post-hoc interpretation.

## Core Comparison

ARK-DM-1 compares three model families:

1. Visible-matter-only baseline.
2. Standard halo-style baseline.
3. Ark-inspired hidden-inheritance correction term.

## Model 1: Visible-Matter-Only Baseline

The visible-matter-only baseline uses the baryonic rotation contribution available from the SPARC data.

This model represents the prediction made from visible matter alone.

Expected output:

- predicted rotation velocity,
- observed rotation velocity,
- prediction error per radial point,
- galaxy-level error summary.

## Model 2: Standard Halo-Style Baseline

A standard dark-matter halo-style baseline may be included if it can be implemented cleanly from the available public data.

Possible halo models include:

- NFW,
- Burkert,
- pseudo-isothermal.

The selected halo model must be documented before final result interpretation.

If a halo model cannot be implemented reproducibly without excessive tuning, ARK-DM-1 may report only the visible-matter baseline and Ark-inspired term, with the limitation clearly stated.

## Model 3: Ark-Inspired Hidden-Inheritance Term

The Ark-inspired term is a measurable correction term inspired by the former Ark / UIP language of hidden inheritance, residual influence, coherence support, and unseen burden.

It must be expressed mathematically using public observables.

Potential observables may include:

- baryonic radial distribution,
- disk scale length,
- gas distribution,
- residual acceleration structure,
- density-gradient style terms,
- radial continuity terms.

The term may not use mystical, symbolic, theological, or metaphorical language as evidence.

## Required Rule

The Ark-inspired term must be simple enough to be tested.

It may not win merely by adding excessive free parameters.

Any additional parameter must be disclosed.

## Primary Metric

Primary metric:

Median prediction error across the selected galaxy sample.

The exact error function will be documented in the code and final results.

## Improvement Threshold

The Ark-inspired term must reduce median prediction error by at least 10% compared with the visible-matter-only baseline.

If it does not, it FAILS.

## Novelty Check

If the Ark-inspired term improves over visible matter only but does not meaningfully outperform a standard halo-style model after accounting for complexity, the result will be reported as LIMITED / NON-NOVEL.

## Interpretation Limits

A PASS does not prove dark matter.

A PASS does not prove new physics.

A PASS does not prove Ark or UIP.

A PASS only means this specific mathematical term survived this specific preregistered open-data test.

## Rule

No post-hoc tuning after seeing outcomes.

No changing the model to rescue a failed result.

Publish pass, fail, limited, or hold.
