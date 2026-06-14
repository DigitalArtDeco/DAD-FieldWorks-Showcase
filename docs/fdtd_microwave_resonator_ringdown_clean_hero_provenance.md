# FDTD Microwave Resonator Ringdown Clean Hero Provenance

This note documents the text-free FDTD microwave resonator ringdown animation
used as the DAD FieldWorks website hero visual.

## Asset Set

- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero.gif`
- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero_poster.png`
- `assets/hero/fdtd_microwave_resonator_ringdown_clean_hero_summary.json`

## Script

`scripts/generate_fdtd_microwave_resonator_ringdown_clean_hero.py`

## Numerical Model

- Model family: deterministic 2D FDTD TMz microwave resonator diagnostic.
- Field components in the update: `Ez`, `Hx` and `Hy`.
- Rendered field quantity: signed `Ez`.
- Source: Gaussian-windowed sinusoidal pulse launched from the feed side.
- Geometry: feed guide, coupling slot, rectangular resonator, central post and
  graded-loss edge absorber.
- Boundary note: the edge absorber is a visual diagnostic boundary treatment.
  No CPML claim is made.

The renderer follows the public-safe ringdown model documented by the existing
DAD FieldWorks public FDTD resonator provenance. It performs a deterministic
field update in the public asset script and writes only public hero assets.

## Public Safety

- Private repository read: no.
- Private code executed: no.
- Existing public-safe FDTD generator reused: no.
- External images: none.
- Screen captures: none.
- AI image generation: none.
- Private source code copied: no.
- Text inside generated GIF frames: no.

## File Size Optimization

The GIF is rendered at website-hero size, uses a compact frame count and is
palette optimized during export. The poster is a separate static PNG with no
in-frame text.

## Claim Boundary

This text-free hero animation is a deterministic public-safe FDTD microwave
resonator ringdown diagnostic. It is not external validation, not production
readiness and not a commercial solver equivalence claim.

Copyright &copy; 2026 Harun Aktas. All rights reserved.
