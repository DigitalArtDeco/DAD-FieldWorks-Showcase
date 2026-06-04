# Microwave Cavity Eigenmode Birth

This animation shows a bounded public-safe path from Yee electric unknowns
toward a rectangular PEC cavity eigenmode residual check.

It is generated from deterministic numerical arrays and Python plotting code.
No external images, screenshots, or AI image generation are used.

The visual sequence shows:

1. Yee electric unknowns on a fine rectangular grid.
2. Oriented curl incidence on selected local cells.
3. A bounded prototype sparse structure panel.
4. A standing rectangular PEC cavity field slice.
5. A residual check and analytical reference comparison status panel.

If no public-safe summary data are supplied at generation time, the cavity
field is the canonical rectangular PEC standing-wave slice:

```text
Ez(x,y,t) = sin(pi x / Lx) sin(pi y / Ly) cos(omega t)
```

The sparse structure is a bounded prototype visualization. It is not a
production matrix, not validation evidence, and not a production readiness
claim. It is not a qubit simulation and not a commercial solver equivalence
claim.

No private source code is published by this animation or its generator.

Copyright © 2026 Harun Aktas. All rights reserved.
