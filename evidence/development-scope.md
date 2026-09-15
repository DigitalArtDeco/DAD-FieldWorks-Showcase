# DAD FieldWorks: current development scope

Review date: 15 September 2026.

This summary describes a read only review of the product feature branch, its current Project Master, integration reports, selected source declarations and existing numerical records. It is not a new application acceptance test, solver run or external validation. Private source code, complete reports and raw project data are not distributed here.

## Implemented product scope

| Area | Reviewed capability | Boundary |
| --- | --- | --- |
| Geometry | Retained parametric RF sketch constructions, named parameters, supported planar operations and project persistence. | Bounded PCB and RF authoring, not unrestricted mechanical CAD. |
| Stackup | Two to sixteen conductor layers and interactive through, blind and buried vias. | Supported layer and via representations have explicit geometry constraints. |
| Terminal ports | Physical local contacts, Thevenin source and load descriptions, and a separate RF reference impedance. | These terminals are not calibrated open modal wave ports. No deembedding is claimed. |
| Simulation setup | Explicit open microstrip recommendations, shared standard and advanced setup state, and checks for stale results and exports. | Planning accepts supported straight geometries and a bounded single right angle width transition. Planning does not qualify their RF response. |
| Results | Complex S matrices, Cartesian and Smith views, saved native fields, project reopening and supported Touchstone exports. | Each numerical result retains the scope and status of its own calculation. |
| Materials | Source bound material records and explicit passive isotropic conductivity and multiple pole Debye models integrated with the native solver. | Published observations are distinct from executable models. No automatic fitting or general material accuracy claim is made. Supported port leads retain their lossless reference model. |

The latest integration also repairs applied object movement in the retained construction history, clockwise contour handling, explicit canvas operations, setup diagnostics and precise resource budget entry. These changes do not themselves establish new electromagnetic accuracy results.

## Previously calculated cases

The existing open microstrip setup report records two independent excitations with 24,576 steps each. It reports twelve valid complex S matrix entries across 0.9, 1.7 and 2.8 GHz, native fields, saved views, project reopening and a checked Touchstone file. A separate reconstruction checks the existing numerical records against their native values. Numerical reproduction is not a physical accuracy measurement.

A separate historical closed eight port reference reports 192 valid complex S matrix entries across three frequencies. This is a different bounded internal case. Its count must not be merged with the microstrip result or presented as independent experimental validation.

The latest integration checkpoint performed no new electromagnetic trajectories or physical mode solves. The results described above predate that integration. Their underlying private execution records are not a publicly reproducible dataset supplied by this website.

## Qualification still open

Full external mouse and desktop acceptance of the latest combined workflow remains open, together with a new complete workflow demonstration and its new two excitation completion. General patch qualification remains unresolved. Smooth curved copper surface loss coupling and a generally qualified copper/PTFE coaxial workflow are not established. External validation, production release and commercial qualification are not claimed.

## What visitors can inspect directly

The website presents unchanged original images from the public showcase. Field views and the Smith chart were selected on 13 September 2026. The original desktop clock in those source captures shows 12 September. There is no independently supplied executable build identity for the images, so they are not attributed to the latest product commit.

- The longitudinal and transverse H y views show the same saved step 4096 at 1.023875 ns. Transparent and contour cross sections use different camera perspectives.
- The Smith chart shows S(2,2) of the shielded TEM reference line at 5.500 GHz with a 50 ohm reference.
- The Cartesian view shows a separate Via Transition case in linear magnitude with a 1.700 GHz marker. The website does not invent samples between recorded frequencies.
- The pulse and returning wave diagnostic figures belong to one internal TEM source test family. They are not two independent experimental studies.
- The three analytical spacing records are historical SI Kernel v0.3 reference values, not new full wave calculations.

The earlier public documentation is preserved as context for those images. Its older material and authoring boundaries are not a complete description of the current branch. Original source records retain their original language and wording.

Public image source: [DAD FieldWorks Showcase at the fixed website revision](https://github.com/DigitalArtDeco/DAD-FieldWorks-Showcase/tree/65d7b9b47f2558f7578b1471d2a0f089d717d05d).

The local asset register records original paths and SHA256 hashes. A matching hash establishes file identity, not physical accuracy or release readiness.
