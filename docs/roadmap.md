# Public Roadmap

The public roadmap presents DAD FieldWorks as being developed toward an evidence-controlled full-wave computational electromagnetics solver platform. The roadmap remains public-safe and claim-bounded: it is not a production solver roadmap, not an external validation claim, and not a commercial solver equivalence claim.

## Current Alpha Evidence Layer

The current public-safe state is bounded internal alpha evidence. It includes C++ Resonator Lab Alpha records, candidate eigenpair records, residual diagnostics, residual threshold gate records and analytical comparison gate records.

This layer does not promote a production solver. It does not release private implementation details. It does not execute or claim physical eigenpair acceptance.

## Current Planning Step

The current planning direction is a records-only physical eigenpair acceptance gate. The planned gate concerns schemas, prerequisite evidence requirements, residual threshold pass requirements, analytical comparison pass requirements, acceptance metadata, pass/fail records, blocker records and future audit boundaries.

The public boundary remains planning only:

- no physical eigenpair acceptance execution,
- no physical eigenfrequency acceptance execution,
- no external validation claim,
- no production readiness claim.

## Near-Term Direction

- Harden residual threshold gate records.
- Harden analytical comparison gate records.
- Plan physical eigenpair acceptance gate records without executing acceptance.
- Keep validation and production flags conservative.
- Keep public whitepaper and companion documentation aligned with claim boundaries.

## Mid-Term Direction

- Harden native solver core architecture and artifact replay.
- Document native field component offsets and boundary masks.
- Plan native Yee curl-curl eigenmode prototype evidence requirements.
- Define FDTD reference cases independent of PEC feature tracking.
- Prepare C++ product-core paths only when evidence contracts are strong enough.

## Long-Term Direction

- Build an evidence-controlled full-wave CEM solver platform.
- Create a full eigenmode solver chain under evidence contracts.
- Establish independent FDTD validation cases when appropriate evidence exists.
- Build external comparison workflows only when public evidence supports them.
- Migrate mature research kernels into C++.
- Keep evidence contracts mandatory for all solver families.

## Backend Gate Summary

| Stage | Direction | Public claim boundary |
| --- | --- | --- |
| Current alpha evidence layer | Candidate, residual and analytical comparison records | Bounded internal alpha evidence only |
| Current planning step | Physical eigenpair acceptance gate planning | Planning only, no physical acceptance execution |
| Near term | Residual threshold and acceptance gate hardening | Internal classification only |
| Mid term | Native solver core hardening and artifact replay | No production solver claim |
| Long term | Evidence-controlled full-wave CEM solver platform | Future target, no current production claim |
| Future research route | DGTD and physics-AI backends under evidence contracts | Future route only |

Any future material should preserve the distinction between roadmap direction, internal evidence, validation evidence and production authorization.

Copyright &copy; 2026 Harun Aktas. All rights reserved.
