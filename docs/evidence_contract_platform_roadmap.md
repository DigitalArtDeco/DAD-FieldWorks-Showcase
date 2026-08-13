# Evidence Contract Platform Roadmap

DAD FieldWorks is being shaped toward an evidence-controlled full-wave computational electromagnetics solver platform. The public position is deliberately narrow: the repository presents a public-safe roadmap, diagnostic visualizations, bounded internal alpha evidence paths and public whitepaper material. It is not a production solver release and not validation evidence.

## Evidence-Controlled CEM Direction

The core idea is that a field, eigenpair, spectrum or solver output remains a candidate claim until evidence gates define what it is allowed to say. A trustworthy solver ecosystem should expose residuals, boundary-condition checks, analytical reference error, reproducibility metadata and explicit claim boundaries.

The current public-safe alpha path includes:

- C++ Resonator Lab Alpha records,
- generalized eigenproblem metadata records,
- candidate eigenpair and residual diagnostics,
- residual threshold gate records,
- analytical comparison gate records,
- physical eigenpair acceptance gate planning only.

## Gate Progression

| Step | Meaning | Current public boundary |
| --- | --- | --- |
| Candidate eigenpair | A result that may support a claim later | Bounded internal alpha evidence |
| Residual diagnostic | Compatibility check under stated assumptions | Diagnostic evidence |
| Residual threshold gate | Record layer for residual classification | Internal classification only |
| Analytical comparison gate | Record layer for comparison to a stated reference | Not external validation |
| Physical eigenpair acceptance gate | Planned schema and prerequisite layer | Planning only |
| Claim boundary | Explicit statement of what remains closed | External validation and production closed |

## From Solver Prototype To Evidence Contract Platform

| Layer | Public direction | Claim boundary |
| --- | --- | --- |
| Native solver evidence layer | Candidate records, residual records and analytical comparison records. | Bounded internal alpha evidence path only. |
| C++ product-core direction | Resonator Lab Alpha records, artifact replay and later numerical-kernel integration when evidence permits. | No production numerical kernel claim. |
| Future research backend layer | Future DGTD route and future AI-assisted route under the same evidence contract discipline. | Future research direction only. |

## AI-Assisted Solvers Under Evidence Contract

A future PINN or neural-operator backend should be treated as an untrusted field generator until it passes evidence gates.

The AI is not trusted because it is neural. It is trusted only when its output survives Maxwell residual checks, boundary-condition checks, finite-value checks, reference comparison where available, reproducibility checks and claim-boundary gates.

## Rejection Logic

`ProductionAllowedQ` remains false by default.

Promotion should stay blocked when:

- residuals are too large,
- boundary conditions are violated,
- analytical reference mismatch is unexplained,
- finite-value sanity fails,
- divergence or gauge checks fail,
- physical eigenpair acceptance has not been executed,
- external validation evidence is missing.

## What This Is Not

This roadmap is not a production solver release, not an external validation claim, not a commercial solver equivalence claim, not an AI-backend validation claim and not a DGTD implementation claim. It is a public-safe architecture direction for evidence-controlled computational electromagnetics.

Copyright &copy; 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
