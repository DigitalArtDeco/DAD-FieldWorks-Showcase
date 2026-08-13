# FDTD Resonator Ringdown FFT Provenance

This public visualization was created from numerical 2D FDTD field data
computed for the showcase.

## Numerical Model

- Solver family: 2D FDTD TMz diagnostic.
- Field components: Ez, Hx, and Hy.
- Rendered field quantity: signed Ez.
- Source type: Gaussian-windowed sinusoidal pulse.
- Boundary handling: graded-loss edge absorber. No CPML claim is made.

## Resonator Geometry

The geometry is a line-coupled rectangular resonator-like cavity with PEC-like
walls, a coupling slot, a feed region, and a central post. It is intended as a
public diagnostic geometry for field build-up, coupling, and ringdown behavior.

## Probe Signal And Spectrum

The probe signal is the local Ez value at a fixed observation point in the
resonator region. The FFT spectrum is derived from the recorded time-domain
probe signal. The late-time signal is mean-subtracted, Hann-windowed, and
transformed with a real FFT. The frequency axis is normalized.

## Claim Boundary

This asset is a diagnostic visualization only. It is not validation evidence,
not production readiness, not a qubit simulation, and not a Josephson junction
model.

No external images were used. No screenshots were used. No AI image generation
was used. No private source code is published.

Copyright &copy; 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
