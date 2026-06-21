# PCB 2D Microstrip Scientific Hero Provenance

## Scope

The homepage animation shows a PCB 2D microstrip electric-field magnitude
visualization in the Scientific Field Image Renderer V2 style. It is a public
website preview derived from a PNG frame sequence.

The public animation represents a drive voltage amplitude sweep of a
quasi-static field magnitude grid. It is not a frequency sweep, not a current
sweep, not time-domain propagation, not full wave simulation, not external
validation and not production evidence.

## Source Field

- Source quantity: `electric_field_magnitude_v_per_m`
- Units: `V_per_m`
- Grid dimensions: `151 x 60`
- Domain: `0.003 m x 0.00118 m`
- Style: Scientific Field Image Renderer V2
- Colormap: `dadfw-blue-red-linear-v2`
- Colorbar range: `0` to `12027.9276124 V_per_m`

The source grid is real DAD FieldWorks PCB 2D quasi-static field data from the
internal parameterized microstrip field-grid artifact. The public frame
metadata does not expose local machine paths or internal prompt/task paths.

## Rendering Method

The PNG sequence uses the same public-safe renderer style as the internal
Scientific Field Image Renderer V2 artifact:

- white plot background,
- blue-to-red scalar field map,
- black ground depiction,
- green substrate boundary,
- dark trace overlay,
- numeric axes,
- colorbar,
- fixed 800 x 600 frame size.

The frame sequence uses a smooth cosine drive amplitude envelope from `0.10` to
`1.00` and back to `0.10`. The colorbar range remains fixed across the whole
sequence so the intensity change remains visible. This uses the recorded
quasi-static linear-scaling assumption and does not present the frames as
separate time-domain solver snapshots.

The internal DAD PNG writer wrote the PNG frames. No external image source,
screenshot, generative image tool, Python plotting layer or third-party image
writer was used for the PNG frames.

## Website Preview

The homepage GIF is derived only from the public PNG frame sequence:

`assets/animations/pcb2d_microstrip_field_scientific_v2_sequence/frames/`

The PNG frame sequence is the primary image artifact. The GIF is a compact
website preview only.

## Repository Boundary

The main DAD FieldWorks repository was read for the existing field-grid data
and the internal PNG writer source. It was not modified. All generated outputs
for this public website task were written inside the public showcase repository.

No private source code was copied into this repository.

## Claim Boundary

This animation is an internal PCB 2D quasi-static field visualization. It is not
external validation, not benchmark evidence, not measurement evidence and not
production evidence. It does not claim commercial solver equivalence.

Copyright 2026 Harun Aktas. All rights reserved.
