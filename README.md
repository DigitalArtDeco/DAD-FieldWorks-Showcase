# DAD FieldWorks

**Physics-based electromagnetic engineering for PCB and RF design.**

This repository publishes the official DAD FieldWorks Showcase from DigitalArtDeco Labs UG (haftungsbeschränkt).

DAD FieldWorks combines a DAD-owned full-vector 3D Yee FDTD core, scientific field visualization, RF result processing and evidence-bound engineering in an integrated native desktop Workbench.

## Implemented Engineering Capabilities

### Native True-3D Electromagnetic Simulation

The C++ time-domain core represents Ex, Ey, Ez, Hx, Hy and Hz at their native staggered Yee locations and advances them through explicit leapfrog updates. The implemented architecture includes component-native material mapping, electric PEC enforcement, source coupling, material-aware CPML infrastructure, native field snapshots and two-port voltage and current acquisition.

An internally exercised PCB reference case completed 4,096 transient steps, saved five full-vector field states and recorded two raw Port V/I traces with 4,096 samples each.

### Scientific Field Visualization

The native wxWidgets Workbench embeds VTK for scientific 3D visualization. Its scientific view combines DAD-owned PCB geometry with field datasets and supports component-native signed scalar slices, derived collocated vector magnitude, vector glyphs, magnitude isosurfaces, engineering units, axes, camera controls, clipping, picking and explicit frame selection.

### Port Signals and RF Processing

DAD FieldWorks records port voltage from native electric-field paths and current from native magnetic-field contours. The downstream RF core provides Yee-aware temporal alignment, deterministic direct Fourier transformation, real-reference power-normalized pseudowaves and structured one-port and two-port processing. Reciprocity, passivity and losslessness diagnostics classify supported result datasets.

### S-Parameter Result Workbench

The native Result Workbench presents versioned complex S-parameter datasets through Matrix, Cartesian and Smith-chart views. The Matrix view exposes response and excitation entries at a selected frequency. Cartesian views provide selectable magnitude, phase, real and imaginary traces with exact markers. The Smith-chart view presents diagonal reflection traces with gamma and normalized-impedance readout. Reference impedance, reference plane data and dataset provenance remain explicit.

### Quasi-TEM Cross-Section Analysis

DAD FieldWorks implements evidence-bound C++ foundations for lossless two-conductor quasi-TEM cross-section analysis. Paired electrostatic and vacuum-companion magnetic formulations record iterations, residuals, convergence thresholds and finite-value checks. Consistency diagnostics connect voltage, charge, current, flux, energy and native staggered fields.

### Evidence-Bound Engineering

Controlled computations bind versioned inputs, solver and executable provenance, execution context, immutable numerical payloads, evaluation records and claim boundaries into a traceable evidence chain. Incomplete or contradictory evidence fails closed.

### Native Engineering Workbench

DAD FieldWorks uses wxWidgets for its native desktop shell, DAD-owned engineering models and a dedicated PCB canvas. VTK provides the scientific visualization backend, while solver, project, result and presentation contracts remain separated from the desktop toolkit.

## Canonical-Yee Field Visualization

The four public captures below show progressively later saved states from one internally exercised Canonical-Yee PCB reference package. Each image uses the same Z-oriented slice and quantitative V/m scale.

| Frame 2/5: Step 924 | Frame 3/5: Step 1109 (Primary view) |
| :---: | :---: |
| [![DAD FieldWorks Canonical-Yee electric-field magnitude, Z slice, saved frame 2 of 5, step 924.](assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-02.png)](assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-02.png) | [![DAD FieldWorks Canonical-Yee electric-field magnitude, Z slice, saved frame 3 of 5, step 1109.](assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-03.png)](assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-03.png) |
| An early saved field state on the selected Z slice. | The field concentration develops along the trace while geometry, slice position and V/m scale remain inspectable. |
| **Frame 4/5: Step 1294** | **Frame 5/5: Step 4095** |
| [![DAD FieldWorks Canonical-Yee electric-field magnitude, Z slice, saved frame 4 of 5, step 1294.](assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-04.png)](assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-04.png) | [![DAD FieldWorks Canonical-Yee electric-field magnitude, Z slice, saved frame 5 of 5, step 4095.](assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-05.png)](assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-05.png) |
| A later saved state on the same comparison scale. | The final stored state in the sequence shows the late-time spatial field distribution across the PCB structure. |

## Evidence Model

```text
Versioned Inputs -> Guarded Execution -> Immutable Payload -> Numerical Evaluation -> Claim Boundary
```

The evidence model keeps numerical output, provenance, evaluation and public claim scope connected without treating visual plausibility as proof.

## Public Repository

This repository contains the static Showcase website, public documentation and approved public-safe technical assets. The private implementation and private engineering evidence remain outside this repository.

## Technical Materials

| Material | Link |
| --- | --- |
| Public website | [https://www.dadlabs.de/](https://www.dadlabs.de/) |
| Company | DigitalArtDeco Labs UG (haftungsbeschränkt) |
| Principal public contact | [info@dadlabs.de](mailto:info@dadlabs.de) |
| Evidence Contract Architecture | [docs/evidence_contract_architecture.md](docs/evidence_contract_architecture.md) |
| Current Implemented Capabilities | [docs/current_public_status.md](docs/current_public_status.md) |
| Claim Boundaries | [docs/claim_boundaries.md](docs/claim_boundaries.md) |
| Canonical-Yee Screenshot Manifest | [assets/images/dad-fieldworks/canonical-yee/manifest.json](assets/images/dad-fieldworks/canonical-yee/manifest.json) |
| Canonical-Yee Visualization Provenance | [docs/canonical_yee_field_visualization_provenance.md](docs/canonical_yee_field_visualization_provenance.md) |
| Asset Manifest | [assets/asset_manifest.md](assets/asset_manifest.md) |

## Legal

- [Impressum](impressum.html)
- [Datenschutz](datenschutz.html)
- [COPYRIGHT.md](COPYRIGHT.md)
- [LICENSE_NOTICE.md](LICENSE_NOTICE.md)

Copyright &copy; 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
