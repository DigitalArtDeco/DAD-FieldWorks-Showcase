# DigitalArtDeco Labs

DigitalArtDeco Labs develops scientific software for electromagnetic simulation and RF engineering. Our work connects numerical methods, PCB and RF workflows, and technical visualization.

[Company website](https://www.dadlabs.de/) · [Contact](mailto:info@dadlabs.de)

## DAD FieldWorks

DAD FieldWorks is our software project for PCB and RF simulation. The Windows application combines supported geometry editing, material and layer definitions, calculations and result inspection.

The current company presentation uses five supplied images: Tuto construction and sketching, plus Via Transition port responses and a saved magnetic field. They document different projects, not one continuous modeling example.

DAD FieldWorks is in development. External validation is not yet complete, and it is not released for production use. The website's outlook describes future goals, not capabilities available today. This repository provides neither the application nor a software download.

## Public documentation

- [Current product scope](docs/current_public_status.md)
- [Technical claim boundaries](docs/claim_boundaries.md)
- [Current screenshot provenance](docs/company_screenshot_provenance.md)
- [Documentation and historical records](docs/README.md)

## Website checks and publication

Run `python scripts/validate_native_workbench_preview.py` for offline image-integrity, link, metadata, copy, privacy and legal checks. After editing the current Markdown notes, run `python scripts/render_public_notes.py` to refresh their styled HTML pages using the existing markdown-it-py development dependency. No browser dependency is introduced.

The site uses static HTML, CSS, local images and Organization JSON-LD. It has no executable page JavaScript or external runtime assets. A user-requested abstract product illustration is documented separately from the unchanged application screenshots.

The existing `main` branch and its configured upstream publish the repository root through GitHub Pages. Domain and hosting configuration are unchanged. See [publication notes](docs/publication_notes.md). A website publication is not a software release.

## Contact and legal

[info@dadlabs.de](mailto:info@dadlabs.de) · [+49 176 48296275](tel:+4917648296275)

[Impressum](impressum.html) · [Datenschutz](datenschutz.html) · [Copyright](COPYRIGHT.md) · [License notice](LICENSE_NOTICE.md)

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
