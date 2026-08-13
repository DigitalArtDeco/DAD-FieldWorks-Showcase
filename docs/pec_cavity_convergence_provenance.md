# PEC Cavity Convergence Provenance

## Generation Method

The PEC Cavity Convergence Plot is generated deterministically with Python.

No external images were used. No screenshots were used. No generative image tools were used. No private source code is published.

## Reference Case

The diagnostic uses a rectangular PEC cavity reference:

- Dimensions: 80 mm x 84 mm x 84 mm
- Mode: 111 scalar reference diagnostic
- Speed of light: 299792458 m/s

The analytical reference frequency is computed as:

```text
f_111 = c0 / 2 * sqrt((1/a)^2 + (1/b)^2 + (1/d)^2)
```

The computed analytical reference is 3.143165987 GHz.

## Numerical Method

The numerical sequence uses the exact discrete finite-difference scalar Helmholtz diagnostic for the first homogeneous-Dirichlet scalar mode on a rectangular grid:

```text
lambda_h =
4 / hx^2 * sin(pi / (2 * (Nx + 1)))^2
+ 4 / hy^2 * sin(pi / (2 * (Ny + 1)))^2
+ 4 / hz^2 * sin(pi / (2 * (Nz + 1)))^2

f_h = c0 / (2 * pi) * sqrt(lambda_h)
```

The relative error is:

```text
relative_error = abs(f_h - f_ref) / f_ref
```

## Convergence Data

| Grid | Numerical frequency (GHz) | Relative error (%) |
| --- | ---: | ---: |
| 8^3 | 3.127232556 | 0.506923 |
| 12^3 | 3.135523195 | 0.243156 |
| 16^3 | 3.138695318 | 0.142235 |
| 20^3 | 3.140235798 | 0.093224 |

The relative error decreases monotonically with grid refinement.

## Claim Boundary

This visualization is a bounded scalar PEC diagnostic. It demonstrates a computed convergence trend against an analytical reference. It is not external validation, not production readiness, not a validated eigenmode, and not a full production solver result.

Copyright &copy; 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
