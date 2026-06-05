# Evidence Contract Architecture

The evidence contract architecture is a public description of how numerical execution can be separated from claim status.

An evidence contract records the intended scope of a computation, the assumptions that frame it, the result category, the claim boundary, and the stop conditions that prevent overstatement.

In the current public direction, this means RF, microwave, cavity, resonator, and future quantum-hardware-oriented results should carry structured metadata, evidence rows, gate rows, comparison rows, risk rows, required future work, and explicit claim boundaries.

## Public Companion Summary

The current private project state remains research and development. Internal work includes solver experiments, diagnostic runs, grid and boundary audits, and evidence status checks. This public site does not release private implementation details or internal result files.

The public architecture idea is conservative:

- numerical execution should produce structured evidence records
- claim status should be explicit and separate from the raw computation
- negative claim flags are as important as positive result flags
- diagnostic visuals should be identified as diagnostic visuals
- blocked claims should remain blocked until a public evidence basis exists

This pattern is also the intended public direction for validation-aware RF and quantum hardware design workflows: computed RF, microwave, cavity, resonator, or future quantum-hardware-oriented results should carry evidence level, limitations, and claim boundary.

The same architecture is intended to generalize across backend routes. Classical solver outputs, future DGTD outputs, and future PINN or neural-operator outputs should all remain candidates until evidence rows, residual checks, boundary-condition checks, finite-value sanity checks, reference comparisons where available, and claim gates permit a stronger classification.

See [Evidence contract platform roadmap](evidence_contract_platform_roadmap.md).

## Claim Boundary

These notes describe an architecture pattern. They do not create an external validation claim, a production readiness claim, or a commercial solver equivalence claim.
