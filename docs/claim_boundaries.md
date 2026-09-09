# Claim boundaries

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved, except where an asset manifest identifies a different copyright owner.

Development preview. External validation is not yet complete. Not released for production use.

## Implemented development scope

Public capability wording covers the native Windows project workflow, supported material and stackup authoring, editable and compiled geometry, ports and frequencies, independent solver excitations, actual complex S matrices, separate result viewers, saved native fields, project persistence and bounded Touchstone export.

Five implemented parametric demo families are named in the [current capability summary](current_public_status.md). The five current screenshots show Tuto construction and Via Transition results. They are separate examples. No successful Tuto simulation, material-browser image or additional software feature is inferred from these images.

Implementation, internal test coverage, screenshot publication permission and physical accuracy are different kinds of evidence. None is silently promoted to another.

## Reading the screenshots

- CURRENT means associated with the current simulation inputs. It is not external validation or formal acceptance.
- Tuto shows editable geometry in 3D and in the RF sketcher. The sketcher status reports no results and constraints not evaluated.
- The Via Transition field is the signed magnetic component H_z in A/m, saved step 12288, time 3.071875e-09 s, Z slice 16.
- That field is a stored time-domain state at native Yee coordinates, not a field at a Cartesian or Smith marker frequency.
- Different components, slices and color scales must not be presented as a common-scale temporal sequence.
- The Cartesian plot shows linear magnitude, not dB. Four selected traces connect available samples with straight segments. This is not evidence of a densely sampled sweep.
- The Smith image selects S(2,2) at 2.800 GHz, with Gamma and normalized and ohmic input-impedance readouts using a 50 ohm reference. No measurement correlation is claimed.
- Cartesian and Smith images select different marker frequencies.
- The 3D image shows authoring geometry, not compiled solver geometry. Its color does not establish finite copper conductivity or computed metal losses.

## Material and exchange limits

The described material workflow uses canonical PEC and scalar, isotropic, nondispersive lossless dielectrics, user records and project snapshots. It is not a manufacturer database. Material labels do not add unsupported loss, dispersion or roughness physics.

Touchstone export is for a complete valid actual matrix, one single-terminal TEM or quasi-TEM channel per physical port, and a common constant positive real reference impedance. Coupled multimode export and general native-interface import are not advertised. See the [export scope](current_public_status.md#supported-touchstone-export).

## Future direction

The company homepage separately describes goals for broader construction, multiport studies, material and loss models, printed antennas and result comparison. Those goals do not expand the present capability claims or establish availability, external validation or delivery dates.

## Publication authority

The user authorized the supplied screenshots for a public development preview. Source and derivative SHA-256 values establish file identity, not software acceptance or electromagnetic accuracy.

Executable build provenance was not supplied. The images are not assigned to a product commit or promoted release. This website update neither changes software acceptance records nor grants production authorization.

No universal arbitrary-PCB support, external validation, commercial relationship, bundled result availability, public software download, browser simulation or purchasable license is asserted.

Historical scientific records keep their original provenance and hashes. They are catalogued separately in the [documentation index](README.md) and are not the current product demonstration.
