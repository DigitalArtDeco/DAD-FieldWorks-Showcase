# Current capabilities

Reviewed for the September 2026 development preview.

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved, except where an asset manifest identifies a different copyright owner.

Development preview. External validation is not yet complete. Not released for production use.

## Native project workflow

DAD FieldWorks is a native Windows electromagnetic workbench for PCB and RF development. Supported projects connect ordered materials and stackup, editable conductor geometry, compiled solver geometry, ports and frequencies, simulation jobs, complex S parameters and saved native fields.

The editable geometry and its solver representation are separate. Grid, material and PEC compilation retain geometry approximations and topology checks. These are implementation capabilities, not universal geometric or scientific applicability.

The native simulation workflow configures time-domain jobs and independent excitations. Its complex matrix is computed from actual solver job data in the supported development scope. Invalid frequencies remain visible; missing cells are not silently filled by interpolation or reciprocity.

## Result inspection and persistence

Matrix, Cartesian, Smith and Native Field views expose different parts of a project-linked result. Cartesian, Smith and field viewers are separate resizable native windows. Cartesian traces connect available samples with straight segments. Smith readouts use diagonal reflection for Gamma and normalized impedance.

Saved field components retain native Yee coordinates, component units, saved step and slice selection. The current screenshots show signed Hy in A/m at step 8192 on Z slice 9, and signed Ez in V/m at step 768 on Y slice 10. These time-domain views do not represent the S-parameter marker frequency. They do not share a normalization or form a sequence.

Projects can preserve result references and viewer selections. Reopening checks saved source identity and reuses matching job data without rerunning the solver when those files remain available. Physical input or material changes invalidate current result association and disable current-result export. A name-only edit with unchanged physical inputs can retain a matching result.

CURRENT means input-matched. It is not evidence of external validation, a promoted software release or completed acceptance.

## Parametric demos and materials

The five implemented demo families are:

- Stepped Impedance Quick Tour
- Uniform Shielded TEM Reference Line
- Coupled Line Modal Demo
- Via Transition
- Symmetric Four Port Junction

The public screenshots show the Stepped Impedance Quick Tour. Demo templates open as editable project copies. No precomputed bundled results or public software download is offered by this site.

The material workflow includes immutable canonical PEC and lossless dielectric definitions, user-owned versioned records and independent project-bound snapshots. Dielectric definitions in the shown lossless workflow are scalar, isotropic and nondispersive. PEC is an ideal boundary, not a high-conductivity copper model. The library does not supply manufacturer FR4, Rogers, copper-loss or roughness models.

Stored descriptions do not make unsupported material physics active. Via and port behavior likewise remain within their implemented family and backend limits.

## Supported Touchstone export

The current native interface exports a bounded complete-result subset. It requires:

- A complete valid actual S matrix and available, verified source job data.
- One single-terminal TEM or quasi-TEM channel per physical port.
- One identical, constant positive real reference impedance for all channels.
- The canonical Touchstone 2.1 subset with Hz frequencies, S parameters, real/imaginary values and a full matrix.

The export does not silently renormalize references, interpolate missing results or fill by reciprocity. The Coupled Line Modal Demo's neutral multimode channels are outside this physical-port export subset. General Touchstone import in the native user interface is not claimed.

## Evidence used for this preview

The review separates three sources:

1. User-supplied original captures from 5 September 2026 establish visible UI states and controls.
2. Targeted read-only inspection of local implementation, usage notes and existing internal test reports supports the additional workflow, demo, material and export summaries.
3. Public companion documentation provides background where it remains consistent with that scope.

No solver, native application, acceptance campaign or private test was run for this website update. No private code or internal reports were copied into this repository. Internal test counts are not published as accuracy metrics.

The screenshot package has no supplied executable build provenance. Its captures are therefore not attributed to a specific product commit, accepted candidate or software release.

See [claim boundaries](claim_boundaries.md) and [image provenance](native_workflow_screenshot_provenance.md).
