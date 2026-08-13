# Kernel Wave Hero Brand Provenance

This note documents the public hero graphic used on the DAD FieldWorks website.

## Asset Set

- `assets/hero/dad_fieldworks_kernel_wave_hero.png`
- `assets/hero/dad_fieldworks_kernel_wave_hero.webp`
- `assets/hero/dad_fieldworks_kernel_wave_hero_summary.json`
- `assets/brand/dad_fieldworks_kernel_wave_mark.png`
- `assets/brand/dad_fieldworks_kernel_wave_mark.svg`
- `assets/brand/dad_fieldworks_kernel_wave_mark_poster.png`

## Method

The asset set is created with the deterministic Python script
`scripts/generate_kernel_wave_hero_brand.py`.

The rendered field is a public-safe rectangular PEC cavity mode 111 scalar
slice:

```text
E(x,z) = sin(pi x / a) sin(pi z / d)
a = 0.080 m
b = 0.084 m
d = 0.084 m
mode = 111
```

The visual adds deterministic contour lines, Yee-style sample markers and
abstract evidence nodes. These elements are presentation structure only; they
do not imply a production operator assembly or external comparison result.

Private repository read: no.

Private code executed: no.

Current public safe evidence source: rectangular PEC cavity mode 111 scalar
field specification.

## Public Safety

- External images: none.
- Screen captures: none.
- AI image generation: none.
- Private source code copied: no.
- Private code executed: no.

## Claim Boundary

This is public brand and presentation material derived from a scalar reference
field. It is not external validation evidence, not production readiness
evidence and not a commercial solver equivalence claim.

Copyright &copy; 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
