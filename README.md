# DAD FieldWorks

**Evidence controlled engineering software for computational electromagnetics, RF design and signal integrity.**

Developed by Harun Aktas as an independent software engineering initiative.

DAD FieldWorks is being developed for engineering workflows where computed results are accompanied by source, evidence, reproducibility and claim boundary records before they are trusted.

**Current public status:** bounded internal alpha analytical reference evidence only. No external validation claim. No production readiness claim. No commercial solver equivalence claim.

## What DAD FieldWorks Is

DAD FieldWorks develops evidence controlled engineering software for computational electromagnetics, RF design and signal integrity workflows.

The current public material focuses on source backed analytical reference kernels, bounded alpha diagnostics, evidence gated records and claim aware result handling.

This repository is a public technical presence for selected website, documentation and public-safe technical material. It is not a release of private solver source code.

## Technology Areas

| Area | Current public direction |
| --- | --- |
| Computational Electromagnetics | Numerical field, mode and residual driven workflows. |
| RF and Microwave Engineering | Resonator, cavity and wave structure diagnostics. |
| Signal Integrity | Analytical reference kernels for impedance, width synthesis and coupled line derived quantities. |
| Evidence Contracts | Result records, trust states, reproducibility metadata and claim boundaries. |

## Public Hero Animation

The homepage hero uses a small text-free FDTD microwave resonator ringdown GIF
derived from a sanitized PNG frame sequence. The PNG frames were written with
the DAD internal PNG writer from numeric field matrices computed by the DAD
FieldWorks 2D TMz FDTD kernel.

The animation is public presentation material only. It is not external
validation evidence, not production readiness evidence and not a commercial
solver equivalence claim.

## Evidence Model

A DAD FieldWorks result is not promoted because it looks plausible. It remains bounded until evidence records define what it may claim.

```text
Computation -> Evidence Record -> Reference or Residual Check -> Claim Boundary -> Trust Status
```

The evidence model separates numerical output from trust state, reproducibility metadata and public claim boundaries.

## Current Public State

- Active development by Harun Aktas.
- Internal source backed analytical reference evidence.
- Selected bounded alpha kernels and diagnostic examples.
- No external validation claim.
- No production readiness claim.
- No commercial solver equivalence claim.
- No full wave EM simulation claim for public diagnostic material.

## Technical Materials

| Material | Link |
| --- | --- |
| Public website | [https://www.dadlabs.de/](https://www.dadlabs.de/) |
| Evidence Contract Architecture | [docs/evidence_contract_architecture.md](docs/evidence_contract_architecture.md) |
| Platform Roadmap | [docs/evidence_contract_platform_roadmap.md](docs/evidence_contract_platform_roadmap.md) |
| Current Public State | [docs/current_public_status.md](docs/current_public_status.md) |
| Claim Boundaries | [docs/claim_boundaries.md](docs/claim_boundaries.md) |
| FDTD Ringdown PNG Sequence | [assets/animations/fdtd_ringdown_png_sequence/manifest.json](assets/animations/fdtd_ringdown_png_sequence/manifest.json) |
| FDTD Ringdown Hero Provenance | [docs/fdtd_microwave_resonator_ringdown_clean_hero_provenance.md](docs/fdtd_microwave_resonator_ringdown_clean_hero_provenance.md) |
| Asset Manifest | [assets/asset_manifest.md](assets/asset_manifest.md) |

## Legal

- [Impressum](impressum.html)
- [Datenschutz](datenschutz.html)
- [COPYRIGHT.md](COPYRIGHT.md)
- [LICENSE_NOTICE.md](LICENSE_NOTICE.md)

Copyright &copy; 2026 Harun Aktas. All rights reserved.
