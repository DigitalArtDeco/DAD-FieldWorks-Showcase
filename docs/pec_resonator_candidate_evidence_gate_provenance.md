# PEC Resonator Candidate Evidence Gate Provenance

This public showcase animation is created with deterministic Python numerical
arrays and plotting code. The repaired version uses a custom 3D projected
rectangular PEC cavity view with semi-transparent analytic field slices.

## Reference

- Reference type: analytic rectangular PEC cavity reference.
- Visualization type: 3D rendered rectangular PEC cavity view.
- Cavity dimensions: `a = 0.080 m`, `b = 0.084 m`, `d = 0.084 m`.
- Mode label: TE101 style reference field.
- Field formula: `Ey(x,z,t) = sin(pi x/a) sin(pi z/d) cos(omega t)`.
- Frequency formula: `f_101 = c0 / 2 sqrt((1/a)^2 + (1/d)^2)`.

## Discrete Diagnostic

The candidate field is sampled on a public interior grid. A public scalar
finite difference diagnostic forms `A e` as a minus discrete Laplacian and uses
identity mass `M e = e`.

The candidate eigenvalue is computed with the Rayleigh quotient:

```text
lambda_candidate = (e^T A e) / (e^T M e)
```

The residual is:

```text
r = A e - lambda_candidate M e
```

The normalized residual is:

```text
||r||_2 / ||lambda_candidate M e||_2
```

## Evidence Gate

The evidence gate status is `Candidate / Pending`. The animation is a bounded
diagnostic only. It is not external validation. It is not production readiness.
It is not a validated eigenmode. It is not a full DAD eigenmode solver result.
It is not a qubit simulation.

No external images were used. No screenshots were used. No generative image
tools were used. No private source code is published.

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
