# Eigenpair Residual Evidence Gate Provenance

This public showcase animation is created with deterministic Python numerical
arrays and plotting code.

## Candidate Concept

The animation visualizes a candidate eigenpair as a claim that must be checked
before promotion. The fallback public diagnostic uses a rectangular PEC cavity
scalar candidate on an x-z slice:

```text
e(x,z) = sin(pi x/a) sin(pi z/d)
```

with dimensions `a = 0.080 m`, `b = 0.084 m` and `d = 0.084 m`.

## Layout

The public animation uses explicit pixel safe zones and a readable two-column
dashboard layout. The left panel is reserved for the candidate field slice.
The right side separates the residual equation, residual metrics, bounded
evidence score and final claim gate into distinct cards. Public text is
wrapped or fitted to the panel bounds to avoid overlap in the poster and GIF
frames. The poster is rendered from the final complete state so the computed
bounded diagnostic score and claim gate are visible together.

## Residual

The public scalar diagnostic uses a minus finite difference Laplacian as `A`
and identity mass as `M`. The residual formula is:

```text
r = A e - lambda M e
```

The residual magnitude is:

```text
||r||_2 / max(||lambda M e||_2, tiny)
```

The reference comparison uses:

```text
lambda_ref = (pi/a)^2 + (pi/d)^2
```

## Evidence Score

The evidence score is deterministic and formula based:

```text
evidence_score = 100.0 * (
  0.20 * finite_score +
  0.20 * boundary_score +
  0.35 * residual_score +
  0.25 * reference_score
)
```

The score combines finite value sanity, boundary sanity, residual magnitude
and reference mismatch. It is a bounded diagnostic score only.

## Claim Boundary

The evidence gate status is `bounded diagnostic`. Claim promotion remains
`internal candidate only`.

This animation is not external validation. It is not production readiness. It
is not an eigenmode validation result. It is not a full DAD eigenmode-solver
result. It is not a qubit simulation.

No external images were used. No screenshots were used. No generative image
tools were used. No private source code is published.

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
