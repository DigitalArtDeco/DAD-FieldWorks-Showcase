# Evidence Contract Platform Roadmap

DAD FieldWorks is being shaped into an evidence-controlled computational electromagnetics framework. The public position is deliberately narrow: the repository presents a public-safe roadmap, diagnostic visualizations, and a bounded internal PEC cavity eigenmode evidence path. It is not a production solver release and not validation evidence.

## Evidence-Driven Computational Electromagnetics

The current public-safe milestone is a bounded internal PEC cavity eigenmode prototype path with residual and analytical reference comparison. It is exposed as an Alpha-style evidence path: useful for explaining how evidence rows, residual rows, reference rows, and claim boundaries travel with a result, but not a production solver claim.

## Why This Matters

Computational electromagnetics results can look convincing while still being wrong. A trustworthy solver ecosystem should compute fields, modes, traces, spectra, and RF quantities, but it should also expose residuals, boundary-condition checks, analytical reference error, reproducibility metadata, and explicit claim boundaries.

The evidence contract layer is intended to prevent numerical success from automatically becoming a validation or product claim.

## From Solver Prototype To Evidence Contract Platform

The roadmap has three layers:

| Layer | Public direction | Claim boundary |
| --- | --- | --- |
| Classical solver layer | Bounded PEC cavity path, curl-curl route, mass matrix route, generalized eigenproblem route, residual checks, and analytical comparison records. | Internal Alpha evidence path only. |
| C++ product layer | Resonator Lab Alpha report and replay route, CLI skeleton, artifact replay, and later numerical-kernel integration when evidence permits. | No production numerical kernel claim. |
| Future research backend layer | Future DGTD route and future AI-assisted route using PINN or neural-operator backends under the same evidence contract discipline. | Future research direction only. |

## AI-Assisted Solvers Under Evidence Contract

A future PINN or neural-operator backend should be treated as an untrusted field generator until it passes evidence gates.

The AI is not trusted because it is neural. It is trusted only when its output survives Maxwell residual checks, boundary-condition checks, finite-value checks, reference comparison where available, reproducibility checks, and claim-boundary gates.

| Backend | Status | Evidence gate |
| --- | --- | --- |
| Classical PEC cavity prototype | Internal Alpha evidence path | Residual and analytical comparison |
| C++ CLI skeleton | Replay-only Alpha infrastructure path | Contract and replay checks |
| DGTD backend | Future research route | Discontinuous Galerkin residual and boundary evidence |
| PINN or neural-operator backend | Future research route | Maxwell residual, boundary and reference gates |

## Rejection Logic

`ProductionAllowedQ` remains false by default.

Promotion should stay blocked when:

- residuals are too large,
- boundary conditions are violated,
- analytical reference mismatch is unexplained,
- finite-value sanity fails,
- divergence or gauge checks fail,
- physical eigenpair acceptance is not justified,
- external validation evidence is missing.

## What This Is Not

This roadmap is not a production solver release, not an external validation claim, not a commercial solver equivalence claim, not an AI-backend validation claim, and not a DGTD implementation claim. It is a public-safe architecture direction for evidence-controlled computational electromagnetics.

Copyright &copy; 2026 Harun Aktas. All rights reserved.
