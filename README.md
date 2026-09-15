# DigitalArtDeco Labs

DigitalArtDeco Labs develops scientific software for electromagnetic simulation and RF engineering. Our work connects numerical methods, PCB and RF workflows, and technical visualization.

[Company website](https://www.dadlabs.de/) · [Contact](mailto:info@dadlabs.de)

## DAD FieldWorks

DAD FieldWorks is our software project for PCB and RF simulation. The Windows application combines supported geometry editing, material and layer definitions, calculations and result inspection.

The current company presentation combines model geometry, three saved H_y views and a Smith chart from the Uniform Shielded TEM Reference Line. The Tuto RF sketcher and Via Transition Cartesian plot remain separate examples. The field views show one saved step, not a time sequence or fields at the Smith marker frequency.

DAD FieldWorks is in development. External validation is not yet complete, and it is not released for production use. The current development overview separates implemented capabilities, documented calculations and remaining limits. This repository provides neither the application nor a software download.

## Public documentation

- [Solver Development](solver-development.html): selected internal numerical source checks, with [original image provenance](assets/images/solver-development/manifest.json).

- [Current product scope, reviewed 15 September 2026](evidence/development-scope.md)
- [Earlier public scope for the original images](docs/current_public_status.md)
- [Technical claim boundaries](docs/claim_boundaries.md)
- [Current screenshot provenance](docs/company_screenshot_provenance.md)
- [Documentation and historical records](docs/README.md)

## Website checks and publication

Serve the repository root over HTTP to review the interactive homepage. Original image and document hashes are recorded in `evidence/asset-register.json`; the source dialogs can verify individual image hashes in the browser. The previous `scripts/validate_native_workbench_preview.py` checks the earlier static presentation and its historical image records. Its homepage assumptions predate this interactive design. After editing the older Markdown notes in `docs/`, run `python scripts/render_public_notes.py` to refresh their corresponding HTML pages.

The approved English homepage uses static HTML, CSS, local images and local JavaScript. Result tabs, image zoom, source search, file verification and discrete analytical record selection run in the browser. It has no external runtime dependencies, analytics, forms or live solver execution. The current product review distinguishes implemented scope from previously documented numerical cases and unresolved qualification. A user-requested abstract product illustration is documented separately from the unchanged application screenshots.

The existing `main` branch and its configured upstream publish the repository root through GitHub Pages. Domain and hosting configuration are unchanged. See [publication notes](docs/publication_notes.md). A website publication is not a software release.

## Contact and legal

[info@dadlabs.de](mailto:info@dadlabs.de) · [+49 176 48296275](tel:+4917648296275)

[Impressum (DE)](impressum.html) · [Legal Notice (EN)](legal-notice.html) · [Datenschutz (DE)](datenschutz.html) · [Copyright](COPYRIGHT.md) · [License notice](LICENSE_NOTICE.md)

The English Legal Notice translates the German Impressum. Keep both versions aligned when company details or legal text change. Both pages remain directly accessible from every website footer.

Copyright © 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
