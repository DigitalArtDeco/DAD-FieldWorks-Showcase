# DAD FieldWorks

DAD FieldWorks is a Windows application for RF and PCB engineers investigating supported electromagnetic structures. Model a structure, calculate its response and inspect reflection, transmission and saved field distributions.

Geometry, simulation settings and results stay together in one project.

Development preview. External validation is not yet complete. Not released for production use.

[See the application](https://www.dadlabs.de/) · [Discuss a technical use case](mailto:info@dadlabs.de)

## What you can investigate

- Reflection and transmission between configured ports, using the complex S matrix and Cartesian frequency traces.
- Input reflection and normalized impedance on a Smith chart, for diagonal reflection terms.
- Electric and magnetic field components at saved time steps and selected slices.
- The response after changing supported geometry parameters and recalculating.

The five editable examples cover a stepped-impedance structure, a shielded TEM reference line, coupled lines, a via transition and a symmetric four-port junction. Project material snapshots retain ideal PEC or supported lossless dielectric definitions independently of later library changes.

Relevant input changes mark earlier results stale and block their export as current. Save and reopen matching project results, or export complete results within the documented Touchstone subset.

## Scope and documentation

This repository publishes the static product showcase, not the application or a software download. It contains approved screenshots, public notes and website checks.

- [Current capabilities and export limits](docs/current_public_status.md)
- [Claim boundaries](docs/claim_boundaries.md)
- [Screenshot provenance](docs/native_workflow_screenshot_provenance.md)
- [Documentation index](docs/README.md)

The field screenshots are saved time-domain components, not fields at the S-parameter marker frequency. Their different components and scales do not form a common animation. Screenshot identity does not establish physical accuracy or an executable version.

## Website checks and publication

Run `python scripts/validate_native_workbench_preview.py` for offline link, image, metadata, copy, privacy and legal checks. The site uses static HTML and CSS, local images and Organization JSON-LD. It has no executable page JavaScript or external runtime assets.

The configured release branch publishes the repository root through GitHub Pages. See [publication notes](docs/publication_notes.md) and the [communication review](docs/product_communication_review_2026_09.md). A website publication is not a software production release.

## Contact and legal

[info@dadlabs.de](mailto:info@dadlabs.de) · [+49 176 48296275](tel:+4917648296275)

[Impressum](impressum.html) · [Datenschutz](datenschutz.html) · [Copyright](COPYRIGHT.md) · [License notice](LICENSE_NOTICE.md)

Copyright &copy; 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
