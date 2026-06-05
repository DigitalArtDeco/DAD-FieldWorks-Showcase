# Public Roadmap

The public roadmap presents DAD FieldWorks as an evidence-contract framework for trustworthy computational electromagnetics. The roadmap remains public-safe and claim-bounded: it is not a production solver roadmap, not an external validation claim, and not a commercial solver equivalence claim.

## Current Alpha Evidence Path

The current public-safe milestone is a bounded internal PEC cavity eigenmode prototype path with residual and analytical reference comparison. It is useful as an Alpha-style evidence path because it shows how candidate numerical results can be wrapped with residual rows, comparison rows, reproducibility metadata, and claim boundaries.

This path does not promote a production solver. It does not release private implementation details.

## Near-Term Direction

- Keep the bounded PEC cavity evidence path conservative.
- Continue Resonator Lab Alpha report and artifact replay planning.
- Keep the C++ direction limited to replay and evidence-contract infrastructure until numerical kernel evidence is ready.
- Document residual, boundary-condition, finite-value, reproducibility and reference-comparison gates.
- Keep public whitepaper and companion documentation aligned with claim boundaries.

## Mid-Term Direction

- Formalize the classical solver layer around bounded PEC cavity, curl-curl route, mass matrix route, generalized eigenproblem route, residual checks and analytical comparison.
- Harden artifact replay contracts for Alpha-style reports.
- Prepare a future C++ product layer without claiming a production numerical kernel.
- Define evidence requirements for future DGTD backend routes.
- Define evidence requirements for future PINN and neural-operator backend routes.

## Long-Term Direction

- Generalize the evidence-contract layer around multiple backend families.
- Evaluate future DGTD outputs using discontinuous Galerkin residual and boundary evidence.
- Evaluate future AI-assisted outputs using Maxwell residual, boundary-condition, divergence, energy, finite-value and reference gates.
- Build external comparison workflows only when public evidence supports them.
- Keep production gates closed by default.

## Backend Gate Summary

| Backend route | Public status | Required evidence direction |
| --- | --- | --- |
| Classical PEC cavity prototype | Internal Alpha evidence path | Residual and analytical comparison |
| C++ replay path | Replay-only infrastructure direction | Contract and artifact replay checks |
| DGTD backend | Future research route | Discontinuous Galerkin residual and boundary evidence |
| PINN or neural-operator backend | Future research route | Maxwell residual, boundary and reference gates |

Any future material should preserve the distinction between roadmap direction, internal evidence, validation evidence, and production authorization.
