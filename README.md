# DAD FieldWorks

**DAD FieldWorks turns engineering calculations into evidence gated records.**

The project is being developed toward an evidence controlled CEM and signal integrity platform where a computed width, impedance, mode or field remains a candidate result until source, test, audit, reproducibility and claim boundary records define what it is allowed to say.

**Current public status:** bounded internal alpha analytical reference evidence only. No external validation claim. No production readiness claim. No commercial solver equivalence claim. No full wave EM simulation claim for Signal Integrity examples.

<p align="center">
  <img src="assets/hero/dad_fieldworks_solver_scattering_hero.gif" alt="DAD FieldWorks evidence contract hero animation" width="100%">
</p>

## Live Style Engineering Examples

These examples show source backed internal analytical reference models from the DAD FieldWorks Signal Integrity Kernel v0.3. They are not external validation results, not production use certification and not full wave EM simulations.

The live website consumes [data/dad_signal_integrity_v0_3_examples.json](data/dad_signal_integrity_v0_3_examples.json) through a lightweight local script. No external images, screenshots, third-party embeds or analytics are used.

### Microstrip 50 Ohm Width Synthesis

| Field | Value |
| --- | ---: |
| Target impedance | 50.0 ohm |
| Relative permittivity | 4.3 |
| Substrate height | 1.6 mm |
| Computed trace width | 3.1187 mm |
| Verification impedance | 50.000 ohm |
| Target error | 0.0000 ohm |
| Trust status | INTERNAL_SOURCE_BACKED_INVERSION_READY |

### Signal Integrity v0.3 Capability Map

| Capability | Public status |
| --- | --- |
| Microstrip characteristic impedance | source pinned; implemented; tested; audited; internal only |
| Microstrip width synthesis | source pinned; implemented; tested; audited; internal only |
| IPC-2141A vs Hammerstad-Jensen comparison | source pinned; implemented; tested; audited; internal comparison only |
| Stripline characteristic impedance | source pinned; implemented; tested; audited; internal only |
| Stripline width synthesis | source pinned; implemented; tested; audited; internal only |
| Coupled Line reference model | source pinned; implemented; tested; audited; internal only |
| Differential Pair reference model | source pinned; implemented; tested; audited; internal only |

All capability cards remain not externally validated and not production ready.

### Available Live Examples

| Example | Real public-safe values shown |
| --- | --- |
| IPC-2141A vs Hammerstad-Jensen comparison | 21 audited internal comparison cases; maximum relative deviation 18.5711 percent |
| Stripline analytical reference example | Z0 = 50.0785 ohm for the listed symmetric stripline case; width synthesis check returns 1.000 mm |
| Coupled Line Even/Odd Mode | Z0e = 89.4488 ohm; Z0o = 54.8093 ohm; C = 4.1646; K = 0.2401 |
| Differential Pair Spacing Sweep | Three real spacing rows with Zdiff, Zcommon and K from the audited reference model |

Mode drawings are conceptual illustrations, not full wave field simulations.

### Awaiting Or Future Data

The current public dashboard has real values for the live v0.3 examples above. Beyond v0.3 directions such as dispersion, dielectric loss, conductor loss, roughness, finite thickness expansion, stripline coupled line, GUI, PCB import and external comparison planning remain future routes with no public result shown.

## Other Evidence Gate Diagnostics

Supporting evidence-gate diagnostics remain available below the live Signal Integrity story on the website and through provenance notes. They are diagnostic communication assets only and do not change the claim boundary.

| Supporting material | Link |
| --- | --- |
| PEC Resonator Candidate Provenance | [docs/pec_resonator_candidate_evidence_gate_provenance.md](docs/pec_resonator_candidate_evidence_gate_provenance.md) |
| Eigenpair Residual Evidence Gate Provenance | [docs/eigenpair_residual_evidence_gate_provenance.md](docs/eigenpair_residual_evidence_gate_provenance.md) |
| PEC Cavity Convergence Provenance | [docs/pec_cavity_convergence_provenance.md](docs/pec_cavity_convergence_provenance.md) |

## What This Public Showcase Is Not

DAD FieldWorks public materials show architecture notes, whitepaper material, diagnostic visualizations and public-safe engineering dashboards from a private research and development project.

- No external validation claim.
- No production readiness claim.
- No commercial solver equivalence claim.
- Not full wave EM simulation for Signal Integrity examples.
- Not measurement validation.
- Not production use certification.
- Not a release of private solver source code.

## Public Materials

| Material | Link |
| --- | --- |
| Whitepaper PDF | [DAD FieldWorks Evidence Contract Architecture Whitepaper v0.9](paper/DAD_FieldWorks_Evidence_Contract_Architecture_Whitepaper_v0_9_public.pdf) |
| Live Engineering Examples Provenance | [docs/live_engineering_examples_provenance.md](docs/live_engineering_examples_provenance.md) |
| Signal Integrity Example Data | [data/dad_signal_integrity_v0_3_examples.json](data/dad_signal_integrity_v0_3_examples.json) |
| Evidence Contract Architecture | [docs/evidence_contract_architecture.md](docs/evidence_contract_architecture.md) |
| Evidence Contract Platform Roadmap | [docs/evidence_contract_platform_roadmap.md](docs/evidence_contract_platform_roadmap.md) |
| Current Public Status | [docs/current_public_status.md](docs/current_public_status.md) |
| Claim Boundaries | [docs/claim_boundaries.md](docs/claim_boundaries.md) |
| Public Roadmap | [docs/roadmap.md](docs/roadmap.md) |
| Asset Manifest | [assets/asset_manifest.md](assets/asset_manifest.md) |

## Repository Contents

This public repository contains selected website files, public documentation, public whitepaper PDFs, public-safe visual assets and public-safe example data.

It does not contain private solver source code. It does not contain private validation workbench files. It does not contain commercial tool screenshots. It does not contain reproduced standards, books or textbook figures.

## Legal Links And Copyright

- [Impressum](impressum.html)
- [Datenschutz](datenschutz.html)

See [COPYRIGHT.md](COPYRIGHT.md) and [LICENSE_NOTICE.md](LICENSE_NOTICE.md).
