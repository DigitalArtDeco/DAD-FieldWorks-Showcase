# September 2026 website refresh review

This review covers the public native workflow development preview. It does not confer software acceptance or production authorization.

## Content and source review

Six approved views show Simulation and results, compiled geometry, Cartesian S parameters, Smith reflection, signed Hy and signed Ez. The former field sequence is removed from the homepage, README, current capability summary, active hero documentation and social image metadata. Its historical files, manifest and provenance remain unchanged and are catalogued as historical.

The narrative follows project setup, materials and stackup, editable and compiled geometry, ports and simulation, result inspection, persistence and supported export. Five implemented demo families are named; the captures show only Stepped Impedance Quick Tour.

Additional capability wording was checked against local implementation and existing reports through read-only inspection. No private source text or internal report was published. CURRENT is distinguished from acceptance; saved time-domain components are distinguished from frequency markers. Material and Touchstone scope remain explicit. Executable build provenance was not supplied.

## Image processing

All eight supplied originals matched the source manifest. Six were selected; the redundant Hy window and overlapping-window view were omitted. Five crops remove the taskbar at (0, 0, 1440, 860). The Cartesian crop at (30, 24, 1117, 737) isolates its complete foreground window. Right and bottom coordinates are exclusive.

Full-size crop pixels match the source rectangles, including an independent decoded-pixel check. There is no scientific retouching or generation. The eight published PNG files total 631,186 bytes: six full-size crops and two smaller 720 × 430 previews. Full-resolution PNGs are smaller in bytes than trial reductions for the other four views.

The [image manifest](../assets/images/dad-fieldworks/native-workflow-2026-09/manifest.json) records source and derivative hashes, dimensions, crop, role, caption and alt text. The [provenance note](native_workflow_screenshot_provenance.md) documents interpretation and processing. A 6,033-byte favicon is derived solely from the unchanged existing DAD brand mark.

## Local verification

The revised offline validator preserves public-data, unsupported-claim, PNG structure/CRC, metadata, source-identity, staging and local-link checks. The old four-frame and exact historical-copy expectations are replaced with the approved six-view contract. Clear preview notices are now required. Image mappings, captions, alt text, dimensions, canonical URLs and social metadata are verified against the current manifest.

Browser checks use an isolated headless Edge profile and website-local temporary outputs. The homepage was captured and inspected at 390 × 844, 768 × 1024, 1440 × 900 and 1920 × 1080. All six detail views were checked at mobile and desktop sizes. Checks cover descendant bounds as well as document width, image loading and aspect ratios, visible notices and captions, navigation, keyboard focus, return actions, full-size PNG views and local links.

The initial direct-image browser-icon 404 was fixed with the DAD favicon. The mobile navigation was compacted and oversized preview derivatives were removed. The offline validator passed across 418 public files and 12 protected historical/legal files. The final browser pass completed all four viewports, six detail pages, browser-native pixel zoom and 15 local navigation targets with no page, console or network errors. Browser captures and detailed test output remain in ignored local storage, not in the public publication set.

## Public data and isolation

CNAME, Impressum, Datenschutz, license and copyright files, legal identity audit, historical images and historical provenance retain their original bytes. No PDF is present in the tracked publication set, and none was created. Existing contact information and Organization data are preserved.

No executable page JavaScript, tracker, external font, form backend or new hosting dependency was added. Detail views use ordinary pages and browser-native image zoom.

All writes from this task are confined to the website repository and its own Git administration. Source copies, browser profiles and local audit records remain ignored inside the website workspace. Other DAD worktrees were read-only. No solver, private test, native workbench, acceptance process or software branch was run or modified.

## Changed paths

- `index.html`, `styles.css`, `README.md`, `.gitignore`, `favicon.ico`.
- `docs/README.md`, `docs/current_public_status.md`, `docs/claim_boundaries.md`, `docs/native_workflow_screenshot_provenance.md`, `docs/showcase_refresh_2026_09.md`.
- `assets/asset_manifest.md`, `assets/hero/README.md`.
- `scripts/prepare_showcase_screenshots.py`, `scripts/validate_native_workbench_preview.py`.
- `assets/images/dad-fieldworks/native-workflow-2026-09/`: `manifest.json`, `simulation-results.png`, `compiled-geometry.png`, `cartesian-s-parameters.png`, `smith-chart.png`, `smith-chart-720.png`, `native-hy-field.png`, `native-hy-field-720.png`, `native-ez-field.png`.
- `views/`: `simulation-results.html`, `compiled-geometry.html`, `cartesian-s-parameters.html`, `smith-chart.html`, `native-hy-field.html`, `native-ez-field.html`.

## Publication gate

The verified existing route is the public Showcase repository's main branch and its existing GitHub Pages publication from the root. No remote, account, DNS, permissions or deployment configuration is changed.

This pre-publication record travels with the website commit. Commit, push, deployment and live verification are separate subsequent outcomes and are reported in the task handoff. A push alone is not treated as live deployment evidence.

Copyright (c) 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
