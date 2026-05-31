# Quantum Hardware Oriented Resonator Diagnostics

This directory contains public-safe resonator diagnostics for RF and quantum hardware workflow direction. The visuals are quantum-hardware-oriented because microwave resonators and cavity fields are part of RF engineering workflows around quantum hardware, but they are not qubit simulations.

## Scalar Resonator Mode Diagnostic

Asset: `quantum_hardware_resonator_diagnostic.gif`

Solver or model family: scalar Helmholtz finite-difference eigenmode diagnostic with homogeneous Dirichlet boundary conditions.

Structure type: rectangular microwave cavity resonator.

Rendered quantity: signed scalar field-mode amplitude on three orthogonal slices, animated with a standing-wave phase factor.

## FDTD Microwave Resonator Ringdown

Assets:

- `fdtd_microwave_resonator_ringdown.gif`
- `fdtd_microwave_resonator_ringdown_poster.png`

Solver or model family: 2D FDTD TMz diagnostic with Ez, Hx, and Hy field updates.

Structure type: line-coupled microwave resonator geometry with PEC-like resonator walls, a feed region, a coupling slot, and a central post.

Rendered quantities: signed Ez field, probe Ez trace, and cavity field energy.

Source type: Gaussian-windowed sinusoidal pulse launched from the feed side.

Boundary handling: graded-loss edge absorber. No CPML claim is made.

The large field panel shows signed Ez in the resonator geometry. The probe trace shows the local time-domain response at one observation point. The cavity energy trace shows how field energy builds up after the pulse couples into the resonator and then decays during ringdown.

The animations are generated from numerical field data. No external images were used. No screenshots were used. No AI image generation was used. No private solver source code is published.

These visualizations are diagnostic communication only. They are not validation evidence, not production readiness claims, and not complete quantum hardware design tool claims.

Additional explanation: [FDTD microwave resonator explanation](../../../docs/fdtd_microwave_resonator_explanation.md).

Copyright &copy; 2026 Harun Aktas. All rights reserved.
