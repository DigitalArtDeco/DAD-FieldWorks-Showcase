# PCB Discontinuity Reflection

This animation shows a PCB trace discontinuity reflection diagnostic. A voltage pulse travels along a microstrip-like trace, reaches an impedance step, reflects partially, and transmits partially.

- Modeling family: lossless characteristic-wave transmission-line time-domain update derived from an ideal line model.
- Discontinuity: impedance step from `Z1 = 50 ohm` to `Z2 = 30 ohm`.
- Reflection coefficient used for the diagnostic: `Gamma = -0.25`.
- Rendered quantities: signed voltage along the line, current magnitude along the line, and a space-time voltage diagnostic.
- Incident, reflected, and transmitted components: shown by the moving trace colors and the space-time map.
- Source type: Gaussian voltage pulse launched from the source-side line section.
- Boundary handling: matched terminations at the two line ends.
- Creation method: solver generated numerical PCB discontinuity reflection visualization.
- External source images: none.
- Screenshots: none.
- AI image generation: none.
- Private solver source code published: no.
- Claim boundary: diagnostic visualization only, not validation evidence, not a production readiness claim.

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
