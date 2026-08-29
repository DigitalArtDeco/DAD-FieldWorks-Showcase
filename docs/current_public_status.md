# Current Implemented Capabilities

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved, except where an asset manifest identifies a different copyright owner.

DAD FieldWorks is developed by DigitalArtDeco Labs UG (haftungsbeschränkt). The current public presentation is based on implemented code, focused tests and internally exercised engineering reference cases.

## Native True-3D Electromagnetic Simulation

The DAD-owned C++ time-domain core represents Ex, Ey, Ez, Hx, Hy and Hz on their native staggered Yee lattice positions. Explicit leapfrog updates advance the full-vector field state. The solver architecture includes component-native material mapping, electric PEC enforcement, source coupling, material-aware CPML infrastructure, native field snapshots and two-port voltage and current acquisition.

One internally exercised PCB reference case completed 4,096 transient steps, saved five full-vector field states and produced two raw Port V/I traces with 4,096 samples each.

## Scientific Field Visualization

The native wxWidgets Workbench embeds VTK for scientific 3D views. Implemented presentation modes include component-native signed scalar slices, derived collocated vector magnitude, vector glyphs and magnitude isosurfaces. The view also handles units, color scales, axes, camera controls, clipping, picking and explicit frame selection.

The published Canonical-Yee sequence shows four states from a five-state reference package on one common Z-oriented slice and V/m scale.

## Port Signals and RF Processing

Port voltage is acquired from native electric-field paths and current from native magnetic-field contours. The RF layer provides Yee-aware temporal alignment, deterministic direct Fourier transformation and real-reference power-normalized pseudowaves. Supported one-port and two-port result datasets can be classified with reciprocity, passivity and losslessness diagnostics.

## S-Parameter Result Workbench

The Result Workbench uses a versioned product-owned complex S-parameter model. The Matrix view exposes response and excitation entries at a selected frequency. Cartesian views provide selectable complex traces and exact markers. The Smith-chart view presents diagonal reflection traces with gamma and normalized-impedance readout. Reference-impedance, reference-plane and package provenance remain explicit. Invalid samples remain visible as gaps, and inconsistent or incomplete payloads fail closed.

## Quasi-TEM Cross-Section Analysis

DAD FieldWorks implements C++ foundations for lossless two-conductor quasi-TEM cross-section analysis. Paired electrostatic and vacuum-companion magnetic formulations record iteration, residual, convergence and finite-value diagnostics. Consistency checks connect voltage, charge, current, flux, energy and native staggered fields.

## Evidence-Bound Engineering

Controlled computations bind versioned inputs, solver and executable provenance, execution context, immutable numerical payloads, evaluation records and claim boundaries into a traceable evidence chain. Process journals and transactional payload handling support deterministic, single-use execution records.

## Native Engineering Workbench

wxWidgets provides the native desktop shell. DAD-owned engineering models and a dedicated PCB canvas remain separate from VTK visualization and from solver, result and evidence contracts. This keeps the computational core independent from the desktop presentation layer.
