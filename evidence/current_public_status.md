# DAD FieldWorks: current capabilities

Product notes for the DigitalArtDeco Labs company website, updated 13 September 2026. The implementation scope below was reviewed on 6 September 2026; the subsequently supplied screenshots document visible application states only. This image update does not review or qualify the ongoing product development. The company website’s development direction describes future goals, not additions to this implemented scope.

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved, except where an asset manifest identifies a different copyright owner.

Development preview. External validation is not yet complete. Not released for production use.

## Project workflow

DAD FieldWorks is a native Windows electromagnetic workbench for PCB and RF development. Supported projects connect ordered materials and stackup, editable conductor geometry, compiled solver geometry, ports and frequencies, simulation jobs, complex S parameters and saved native fields.

The editable geometry and its solver representation are separate. Grid, material and PEC compilation retain geometry approximations and topology checks. These are implementation capabilities, not universal geometric or scientific applicability.

The native simulation workflow configures time-domain jobs and independent excitations. Its complex matrix is computed from actual solver job data in the supported development scope. Invalid frequencies remain visible; missing cells are not silently filled by interpolation or reciprocity.

## Result inspection and persistence

Matrix, Cartesian, Smith and Native Field views expose different parts of a project-linked result. Cartesian, Smith and field viewers are separate resizable native windows. Cartesian traces connect available samples with straight segments. Smith readouts use diagonal reflection for Gamma and normalized impedance.

Saved field components retain native Yee coordinates, component units, saved step and slice selection. The three current field images show the Uniform Shielded TEM Reference Line: signed H_y in A/m at saved step 4096, time 1.023875e-09 s. The longitudinal view uses normal Y, index 10; the two transverse views use normal X, index 21. Transparent authoring surfaces and section contours show the spatial context, not solver cell occupancy. These are views of one saved step, not a time sequence or fields at a plot marker frequency.

The current Smith image shows S(2,2) of the same reference project, at 5.500 GHz with a 50 ohm reference and the option Smith: wavelength scales. The outer scales are graphical aids for the displayed lossless-line convention. This image does not establish a separate line-length calculation, deembedding result, new interaction or validation at that frequency. The Via Transition Cartesian plot remains a different result example. Earlier H_z, Hy and Ez captures remain historical records.

Projects can preserve result references and viewer selections. Reopening checks saved source identity and reuses matching job data without rerunning the solver when those files remain available. Physical input or material changes invalidate current result association and disable current-result export. A name-only edit with unchanged physical inputs can retain a matching result.

CURRENT means input-matched. It is not evidence of external validation, a promoted software release or completed acceptance.

## Parametric demos and materials

The five implemented demo families are:

- Stepped Impedance Quick Tour
- Uniform Shielded TEM Reference Line
- Coupled Line Modal Demo
- Via Transition
- Symmetric Four Port Junction

The current images show the Uniform Shielded TEM Reference Line, the Tuto RF sketcher and the Via Transition Cartesian plot. These are distinct examples and do not establish a successful calculation of the Tuto geometry. Demo templates open as editable project copies. Changing supported template parameters regenerates project geometry, stackup and ports. Replacing manual edits requires confirmation. Relevant input changes mark earlier results stale.

No precomputed bundled results or public software download is offered by this site.

The material workflow includes immutable canonical PEC and lossless dielectric definitions, user-owned versioned records and independent project-bound snapshots. Later library changes do not silently modify those snapshots. Dielectric definitions in the shown lossless workflow are scalar, isotropic and nondispersive. PEC is an ideal boundary, not a high-conductivity copper model. The library does not supply manufacturer FR4, Rogers, copper-loss or roughness models.

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

1. Five newly supplied captures selected on 13 September 2026 establish the visible reference-model, field and Smith views. Two earlier captures remain active: the Tuto RF sketcher and Via Transition Cartesian plot. Superseded images and their dated provenance are retained.
2. Targeted read-only inspection of the completed implementation, usage notes and existing internal test reports supports the additional workflow, demo, material and export summaries. The committed scope records internal completion of the five demos, material snapshots and separate result windows; this is not external validation or production authorization.
3. Public companion documentation provides background where it remains consistent with that scope.

No solver, native application, acceptance campaign or private test was run for this website update. No private code or internal reports were copied into this repository. Internal test counts are not published as accuracy metrics.

The screenshot package has no supplied executable build provenance. Its captures are therefore not attributed to a specific product commit, accepted candidate or software release.

See [claim boundaries](claim_boundaries.md), [current image provenance](company_screenshot_provenance.md) and the [historical documentation index](README.md#historical-visual-records).
