# Claim boundaries

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved, except where an asset manifest identifies a different copyright owner.

Development preview. External validation is not yet complete. Not released for production use.

## Implemented development scope

Public capability wording covers the native Windows project workflow, supported material and stackup authoring, editable and compiled geometry, ports and frequencies, independent solver excitations, actual complex S matrices, separate result viewers, saved native fields, project persistence and bounded Touchstone export.

Five implemented parametric demo families are named in the [current capability summary](current_public_status.md). The six current screenshots show one family, Stepped Impedance Quick Tour. No additional demo image, material-browser image or software feature is invented.

Implementation, internal test coverage, screenshot publication permission and physical accuracy are different kinds of evidence. None is silently promoted to another.

## Reading the screenshots

- CURRENT means associated with the current simulation inputs. It is not external validation or formal acceptance.
- Hy is a signed magnetic field component in A/m, saved step 8192, Z slice 9.
- Ez is a signed electric field component in V/m, saved step 768, Y slice 10.
- Both field views are stored time-domain states at native Yee coordinates. They are not automatically fields at a Cartesian or Smith marker frequency.
- Different components, slices and color scales are not a common-scale temporal sequence.
- Cartesian plots connect real available samples with straight segments. They are not evidence of a densely sampled sweep.
- Smith readouts show diagonal reflection, Gamma and normalized impedance. No measurement correlation is claimed.
- Matrix and Smith captures need not show the same selected frequency.
- Geometry color does not establish finite copper conductivity or computed metal losses. The compiled structure is already partly outside its original viewport.

## Material and exchange limits

The described material workflow uses canonical PEC and scalar, isotropic, nondispersive lossless dielectrics, user records and project snapshots. It is not a manufacturer database. Material labels do not add unsupported loss, dispersion or roughness physics.

Touchstone export is for a complete valid actual matrix, one single-terminal TEM or quasi-TEM channel per physical port, and a common constant positive real reference impedance. Coupled multimode export and general native-interface import are not advertised. See the [export scope](current_public_status.md#supported-touchstone-export).

## Publication authority

The user authorized the supplied screenshots for a public development preview. Source and derivative SHA-256 values establish file identity, not software acceptance or electromagnetic accuracy.

Executable build provenance was not supplied. The images are not assigned to a product commit or promoted release. This website update neither changes software acceptance records nor grants production authorization.

No universal arbitrary-PCB support, external validation, commercial relationship, bundled result availability, public software download, browser simulation or purchasable license is asserted.

Historical scientific records keep their original provenance and hashes. They are catalogued separately in the [documentation index](README.md) and are not the current product demonstration.
