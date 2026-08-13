# PEC Resonator Candidate Evidence Gate

This public showcase animation shows a 3D rendered rectangular PEC cavity,
an analytic reference field, a sampled discrete candidate field, a finite
difference residual check and an explicit evidence gate.

The reference is a TE101 style field pattern in a rectangular cavity with
dimensions 80 mm x 84 mm x 84 mm:

```text
Ey(x,z,t) = sin(pi x/a) sin(pi z/d) cos(omega t)
```

The field is created from closed form equations and rendered as
semi-transparent field slices inside the cavity. The discrete candidate
residual is computed from a public finite difference scalar diagnostic. The
candidate eigenvalue and normalized residual are computed by
`scripts/generate_pec_resonator_candidate_evidence_gate.py`.

The evidence gate remains `Candidate / Pending`.

This animation does not require a finished DAD eigenmode solver. It is not a
DAD production eigensolver output. It is not external validation. It is not
production readiness. It is not a commercial solver equivalence claim. It is
not a qubit simulation.

No external images were used. No screenshots were used. No generative image
tools were used. No private source code is published.

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
