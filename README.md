# DAD FieldWorks

**Evidence controlled engineering software for computational electromagnetics, RF design and signal integrity.**

Developed by Harun Aktas as an independent software engineering initiative.

DAD FieldWorks is being developed for engineering workflows where computed results are accompanied by source, evidence, reproducibility and claim boundary records before they are trusted.

**Current public status:** bounded internal alpha analytical reference evidence only. No external validation claim. No production readiness claim. No commercial solver equivalence claim.

## What DAD FieldWorks Is

DAD FieldWorks develops evidence controlled engineering software for computational electromagnetics, RF design and signal integrity workflows.

The current public material focuses on source backed analytical reference kernels, bounded alpha diagnostics, evidence gated records and claim aware result handling.

This repository is a public technical presence for selected website, whitepaper, documentation and public-safe example data. It is not a release of private solver source code.

## Technology Areas

| Area | Current public direction |
| --- | --- |
| Computational Electromagnetics | Numerical field, mode and residual driven workflows. |
| RF and Microwave Engineering | Resonator, cavity and wave structure diagnostics. |
| Signal Integrity | Analytical reference kernels for impedance, width synthesis and coupled line derived quantities. |
| Evidence Contracts | Result records, trust states, reproducibility metadata and claim boundaries. |

## Engineering Examples

The public website includes restrained engineering example panels backed by public-safe data in [data/dad_signal_integrity_v0_3_examples.json](data/dad_signal_integrity_v0_3_examples.json).

The examples show source backed internal analytical reference model outputs. They are not external validation results, not production use authorization and not full wave EM simulations.

| Example | Public-safe values shown |
| --- | --- |
| Microstrip 50 Ohm Width Synthesis | Computed trace width `3.1187 mm`; verification impedance `50.000 ohm`. |
| Analytical Reference Family Comparison | `21` audited internal comparison cases; maximum relative deviation `18.5711 percent`. |
| Stripline analytical reference example | `Z0 = 50.0785 ohm`; width synthesis check returns `1.000 mm`. |
| Coupled Line Even/Odd Mode | `Z0e = 89.4488 ohm`; `Z0o = 54.8093 ohm`; `C = 4.1646`; `K = 0.2401`. |
| Differential Pair Spacing Sweep | Three spacing rows with `Zdiff`, `Zcommon` and `K` from the audited reference model. |

Small technical diagrams are conceptual illustrations only.

## Public Hero Graphic

The website hero graphic is created deterministically with Python from a
public-safe rectangular PEC cavity mode 111 scalar field slice. It uses no
external images, no screen captures and no AI image generation.

The graphic is public brand material only. It is not external validation
evidence, not production readiness evidence and not a commercial solver
equivalence claim.

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
- No full wave EM simulation claim for Signal Integrity examples.

## Technical Materials

| Material | Link |
| --- | --- |
| Public website | [https://www.dadlabs.de/](https://www.dadlabs.de/) |
| Whitepaper PDF | [DAD FieldWorks Evidence Contract Architecture Whitepaper v0.9](paper/DAD_FieldWorks_Evidence_Contract_Architecture_Whitepaper_v0_9_public.pdf) |
| Evidence Contract Architecture | [docs/evidence_contract_architecture.md](docs/evidence_contract_architecture.md) |
| Platform Roadmap | [docs/evidence_contract_platform_roadmap.md](docs/evidence_contract_platform_roadmap.md) |
| Current Public State | [docs/current_public_status.md](docs/current_public_status.md) |
| Claim Boundaries | [docs/claim_boundaries.md](docs/claim_boundaries.md) |
| Engineering Example Provenance | [docs/live_engineering_examples_provenance.md](docs/live_engineering_examples_provenance.md) |
| Kernel Wave Hero Provenance | [docs/kernel_wave_hero_brand_provenance.md](docs/kernel_wave_hero_brand_provenance.md) |
| Public Example Data | [data/dad_signal_integrity_v0_3_examples.json](data/dad_signal_integrity_v0_3_examples.json) |
| Asset Manifest | [assets/asset_manifest.md](assets/asset_manifest.md) |

## Legal

- [Impressum](impressum.html)
- [Datenschutz](datenschutz.html)
- [COPYRIGHT.md](COPYRIGHT.md)
- [LICENSE_NOTICE.md](LICENSE_NOTICE.md)

Copyright &copy; 2026 Harun Aktas. All rights reserved.
