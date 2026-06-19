# FDTD Microwave Resonator Ringdown Hero Provenance

This note documents the public website hero animation for the DAD FieldWorks
showcase site.

## Asset Set

- `assets/animations/fdtd_ringdown_png_sequence/frames/`
- `assets/animations/fdtd_ringdown_png_sequence/manifest.json`
- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero.gif`
- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero_poster.png`
- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero_summary.json`

## Source Chain

The primary artifact is the ordered PNG frame sequence. The public GIF is a
derived website preview created only from the sanitized public PNG frames.

```text
DAD FDTD microwave resonator ringdown solver output
-> audited internal DAD PNG writer
-> ordered PNG frame sequence
-> sanitized public PNG frame sequence
-> optimized website GIF preview
```

## Frame Sequence

- Frame count: 64.
- Public frame dimensions: 720 x 405 px.
- GIF dimensions: 640 x 360 px.
- Source field quantity: signed `Ez` field.
- Ringdown case: rectangular PEC microwave resonator with internal PEC post.
- PEC object confirmed: yes.
- In-frame text: none.
- Screenshots used: no.
- External images used: no.
- AI image generation used: no.
- External plotting tools used: no.
- Internal PNG writer confirmed: yes.

## GIF Packaging

The GIF was packaged in the public showcase repository by
`scripts/package_fdtd_ringdown_png_sequence_to_gif.py`. The script reads only
the sanitized public PNG frames, resizes them for website use, applies GIF
palette optimization, writes the poster frame and writes the summary JSON.

The packaging script does not compute field data, does not read private source
code, does not use screenshots, does not use external images and does not use
AI image generation.

## Evidence Status

- `DerivedWebsitePreviewFromPngFramesQ`: true.
- `PrimaryEvidenceArtifact`: `PNGFrameSequence`.
- `GifIsEvidenceArtifactQ`: false.
- `ExternalValidationQ`: false.
- `ProductionAllowedQ`: false.

The GIF is a public website preview only. The PNG frame sequence remains the
primary evidence artifact for this visual.

## Claim Boundary

This GIF is a derived public website preview from PNG frames written by the DAD
PNG writer from internal FDTD microwave resonator ringdown solver output. It is
not external validation, not measurement evidence, not benchmark evidence and
not production evidence.

Copyright &copy; 2026 Harun Aktas. All rights reserved.
