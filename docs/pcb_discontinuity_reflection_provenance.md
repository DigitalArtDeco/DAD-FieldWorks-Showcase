# PCB Discontinuity Reflection Provenance

The PCB discontinuity reflection animation is generated from numerical time-domain line data for a public-safe diagnostic visualization.

## Numerical Family

- Modeling family: lossless characteristic-wave transmission-line time-domain update derived from an ideal line model.
- Trace discontinuity type: impedance step.
- Impedance values: `Z1 = 50 ohm`, `Z2 = 30 ohm`.
- Reflection coefficient used for the diagnostic: `Gamma = -0.25`.
- Rendered quantities: signed voltage along the line, current magnitude along the line, and a space-time voltage diagnostic.
- Source type: Gaussian voltage pulse launched from the source-side line section.
- Boundary handling: matched terminations at the two line ends.
- Simulation steps: 1800.
- Rendered frames: 180 frames at 15 frames per second.

## Public Boundary

- External source images: none.
- Screenshots: none.
- AI image generation: none.
- Private source code published: no.
- Claim boundary: diagnostic visualization only, not validation evidence, not a production readiness claim.

Copyright © 2026 Harun Aktas. All rights reserved.
