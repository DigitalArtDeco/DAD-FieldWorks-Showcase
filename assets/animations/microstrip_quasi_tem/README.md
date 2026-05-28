# Microstrip Quasi TEM Cross Section

This animation shows a quasi TEM microstrip cross-section diagnostic. The visible structure contains a top conductor trace, a dielectric substrate, and a lower ground plane.

The numerical model is a finite-difference quasi-static cross-section solve of `div(epsilon grad V) = 0`. The top trace is held at 1 V, the ground plane is held at 0 V, and the domain contains dielectric substrate and air regions. Electric field vectors are computed as `E = -grad(V)`.

Rendered quantities:

- Electric potential and electric-field energy density.
- Electric field lines derived from the computed E field.
- Field concentration and fringing near the trace edges.
- A voltage ramp from near 0 V to 1 V for readable animation of field growth.

No external images were used. No screenshots were used. No AI image generation was used. No private solver source code is published.

This is a diagnostic visualization only. It is not validation evidence, not a production readiness claim, and not a full wave solver claim.

Copyright © 2026 Harun Aktas. All rights reserved.
