# FDTD Resonator Ringdown With FFT Spectrum

This animation shows a public-safe 2D FDTD TMz microwave resonator diagnostic.
It renders field build-up, late-time ringdown, a probe Ez time trace, cavity
field energy, and an FFT spectrum derived from the time-domain probe signal.

Solver or model family: 2D FDTD TMz diagnostic with Ez, Hx, and Hy field
updates.

Geometry type: line-coupled rectangular resonator-like cavity with PEC-like
walls, a coupling slot, a feed region, and a central post.

Field quantity rendered: signed Ez.

Source type: Gaussian-windowed sinusoidal pulse launched from the feed side.

Boundary handling: graded-loss edge absorber. No CPML claim is made.

Probe signal: the local Ez value at a fixed observation point inside the
resonator region was recorded over the full numerical time history.

FFT derivation: the late-time probe signal was mean-subtracted, Hann-windowed,
and transformed with a real FFT. The frequency axis is normalized.

This diagnostic is relevant to RF and quantum-hardware-oriented microwave
resonator workflows because it shows classical field storage, coupling,
ringdown, and spectral response around a resonator-like structure. It is not a
qubit simulation and not a Josephson junction model.

The visualization is not validation evidence and not production readiness.

No external images were used. No screenshots were used. No AI image generation
was used. No private solver source code is published.

Assets:

- `fdtd_resonator_ringdown_fft.gif`
- `fdtd_resonator_ringdown_fft_poster.png`

Copyright &copy; 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
