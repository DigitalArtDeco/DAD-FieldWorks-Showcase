# PEC Cavity Visualization Provenance

The PEC cavity animation is generated from numerical eigenmode field data for a public-safe diagnostic visualization.

## Numerical Family

- Solver or modeling family: scalar Helmholtz finite-difference eigenmode with homogeneous Dirichlet boundary conditions.
- Cavity dimensions: `a = 0.08 m`, `b = 0.084 m`, `d = 0.084 m`.
- Boundary conditions: scalar homogeneous Dirichlet on all six cavity faces.
- Mode indices: `{1, 1, 1}`.
- Grid used for visualization: `{27, 24, 24}`.
- Rendered quantity: signed scalar eigenmode amplitude with standing-wave phase factor.
- Slice planes: xy at `z = d/2`, xz at `y = b/2`, and yz at `x = a/2`.
- Numerical frequency used: `3.141247276061735 GHz`.
- Reference frequency for the public PEC cavity case: `3.143165987503105 GHz`.

## Public Boundary

- External source images: none.
- Screenshots: none.
- AI image generation: none.
- Private source code published: no.
- Claim boundary: diagnostic visualization only, not validation evidence, not a production readiness claim.
- Scalar boundary: not a full vector Maxwell eigenmode claim.

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
