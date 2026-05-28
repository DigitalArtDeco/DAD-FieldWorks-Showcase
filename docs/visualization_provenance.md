# Visualization Provenance

The hero animation and poster are generated from numerical field data for a public-safe diagnostic visualization.

## Field Family

The rendered diagnostic follows a 2D FDTD TMz field family with Ez, Hx, and Hy updates. The public asset renders the signed Ez field.

## Geometry

The simulation includes a rectangular PEC-like object inside the computational domain. Ez is held at zero inside the PEC mask, and the rendered object outline comes from that mask.

## Source

The incident field is driven by a Gaussian-modulated sine soft source positioned left of the PEC object. The resulting frames show the incoming wave, object interaction, reflection, scattering, and shadowing.

## Boundary Handling

The diagnostic uses a conservative graded-loss boundary treatment with a simple absorbing edge copy. The visualization is chosen so the object interaction is visible before outer-boundary effects dominate the frame.

## Claim Boundary

This visualization is a solver generated diagnostic asset for public presentation. It is not validation evidence, not a production readiness claim, and not an external solver equivalence claim.

No external images, screenshots, or AI image generation were used. No private solver source code is published in this repository.

Copyright © 2026 Harun Aktas. All rights reserved.
