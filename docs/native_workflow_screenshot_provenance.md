# Native workflow screenshot provenance

Capture date: 5 September 2026.

Owner: DigitalArtDeco Labs UG (haftungsbeschränkt).

Publication authority: the user supplied eight original PNGs and a source manifest and explicitly authorized their use for this development preview. All eight files matched the supplied SHA-256 values, byte sizes and 1440 × 900 dimensions. The corresponding clipboard attachments were byte-identical.

## Selected publication views

Crop coordinates are `(left, top, right, bottom)`, with right and bottom exclusive.

| Source | Publication view | Crop | Full derivative |
| --- | --- | --- | --- |
| `01-main-current-viewer-actions.png` | Hero, complex matrix and viewer actions | (0, 0, 1440, 860) | 1440 × 860 PNG |
| `Screenshot (13).png` | Compiled geometry | (0, 0, 1440, 860) | 1440 × 860 PNG |
| `Screenshot (10).png` | Complete foreground Cartesian window | (30, 24, 1117, 737) | 1087 × 713 PNG |
| `Screenshot (4).png` | Smith chart | (0, 0, 1440, 860) | 1440 × 860 PNG |
| `Screenshot (7).png` | Signed Hy, A/m, step 8192, Z slice 9 | (0, 0, 1440, 860) | 1440 × 860 PNG |
| `Screenshot (6).png` | Signed Ez, V/m, step 768, Y slice 10 | (0, 0, 1440, 860) | 1440 × 860 PNG |

The five maximized/main-window crops remove only the Windows taskbar. The Cartesian crop retains the entire foreground window, including its title, status, chart, legend and footer, while excluding unrelated background windows.

`Screenshot (11).png` is omitted because it repeats the Hy viewer with little additional explanatory value. `Screenshot (8).png` is omitted because the overlapping windows obscure important result content.

## Processing and identity

All preparation used copies inside an ignored website-local staging directory. The originals at their source location remained byte-identical. No source image is linked into the site through a filesystem link.

Full-size crop pixels were compared against the corresponding original rectangle. PNG optimization and omission of metadata preserve those pixels. Two additional 720 × 430 PNGs are downscaled responsive previews for Smith and Hy, not new scientific data. For the other four views, the full-resolution PNG compresses to fewer bytes than its downscaled trial, so the smaller full-resolution file is used at every screen size.

The [machine-readable manifest](../assets/images/dad-fieldworks/native-workflow-2026-09/manifest.json) records source name, SHA-256, dimensions, crop, role, caption and alt text, plus each derivative's dimensions, byte count, file SHA-256 and decoded RGBA pixel SHA-256. Crops and originals have different file hashes; no byte-identity claim is made between them.

No generative processing, retouching, recoloring, curve smoothing, extra samples, sharpening, upscaling or screenshot compositing was used. The taskbar-bearing desktop originals are not part of the public commit.

## Interpretation

These views all show the Stepped Impedance Quick Tour. They are not a continuation of the former field sequence.

Hy and Ez retain their signed component units, native Yee placement, saved time step, slice, axes and scales. They are separate time-domain inspections, not fields at the S-parameter marker frequency and not common-scale comparisons.

The Cartesian plot uses the available samples joined by straight segments. The Smith view exposes diagonal reflection and normalized impedance. It need not select the same frequency as the matrix capture.

The conductor geometry remains partly outside the original viewport. Its display color is not evidence of copper conductivity or metal loss.

Visible Development, CURRENT and unsaved-state labels are retained. CURRENT means input-matched, not externally accepted.

## Development authority and privacy

Development preview. External validation is not yet complete. Not released for production use.

Executable build provenance was not supplied with the captures. No association with a product commit or software release is asserted. File identity does not establish accuracy or acceptance.

Public manifests contain neutral source filenames, image hashes and image metadata. Private filesystem paths, source code, execution records and internal source-to-implementation mappings are not published.

Copyright (c) 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.
