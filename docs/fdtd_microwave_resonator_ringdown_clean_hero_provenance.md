# FDTD Microwave Resonator Ringdown Hero Provenance

This note documents the text-free FDTD microwave resonator ringdown animation used as the DAD FieldWorks website hero visual.

## Public Assets

- `assets/animations/fdtd_ringdown_png_sequence/frames/`
- `assets/animations/fdtd_ringdown_png_sequence/manifest.json`
- `assets/animations/fdtd_ringdown_png_sequence/metadata/`
- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero.gif`
- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero_poster.png`
- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero_summary.json`

## Generation Path

The numeric field matrices were computed by the DAD FieldWorks 2D TMz FDTD kernel in a read-only execution of the main project code. The matrices were written into a public-repository temporary folder. A public-side C++ wrapper then rendered those matrices through the DAD internal PNG writer.

The website GIF was derived only from the sanitized public PNG frames by `scripts/package_fdtd_ringdown_png_sequence_to_gif.py`.

```text
DAD FDTD solver output
-> DAD internal PNG writer
-> ordered public PNG frame sequence
-> derived website GIF
```

## Frame Set

- Frame count: 48.
- PNG frame dimensions: 720 x 405 px.
- GIF dimensions: 640 x 360 px.
- Source field quantity: signed `Ez`.
- Source grid: 2D TMz Yee grid.
- PEC object confirmed: yes.
- In-frame text: no.

## Public Safety

- Private repository read: yes, for read-only package execution and internal PNG writer source compilation.
- Private code executed: yes, through read-only DAD FDTD package execution and the internal PNG writer source linked into a public temporary build.
- Private source code copied into public tracked files: no.
- External images: none.
- Screenshots: none.
- AI image generation: none.
- GIF source: sanitized PNG frame sequence only.
- GIF evidence status: website preview only.
- Primary image artifact: PNG frame sequence.

## Claim Boundary

This public website animation is an internal research visualization based on DAD FDTD field data and DAD internal PNG writer frame evidence. It is not external validation, not benchmark evidence, not measurement evidence and not production evidence.

Copyright (c) 2026 Harun Aktas. All rights reserved.
