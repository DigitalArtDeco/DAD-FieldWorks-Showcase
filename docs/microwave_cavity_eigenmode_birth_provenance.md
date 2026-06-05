# Microwave Cavity Eigenmode Birth Provenance

This public showcase animation is generated from deterministic numerical
arrays and public-safe Python plotting code.

The animation uses a rectangular PEC cavity surrogate and visualizes:

1. Yee electric unknowns.
2. Oriented curl incidence.
3. Sparse matrix style signed incidence entries with cyan `+1` cells,
   orange `-1` cells, and faint gray empty cells.
4. Bounded curl-curl structure, marked as prototype only.
5. Standing eigenmode field slice.
6. Residual and analytical reference comparison panel.

The generator can optionally consume public-safe summary values supplied at
generation time, read only, for the residual and reference status labels. It
does not require that data. Without supplied summary values, it renders a
canonical rectangular PEC standing-wave field:

```text
Ez(x,y,t) = sin(pi x / Lx) sin(pi y / Ly) cos(omega t)
```

The claim boundary is conservative: bounded internal prototype visualization
only. This page makes no external validation claim, no production readiness
claim, no arbitrary geometry support claim, no CPML support claim, no qubit
simulation claim, and no complete quantum hardware solver claim.

No external images are used. No screenshots are used. No AI image generation
is used. No private source code is published.
