#!/usr/bin/env python3
"""Validate the public Canonical-Yee Workbench showcase update.

The validator is intentionally standard-library only and offline.  It checks
the four losslessly published screenshots, their manifest and chronological
presentation, accessibility/metadata requirements, local link integrity, and
the bounded public-copy contract requested for this publication tranche.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
import sys
import zlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIR = ROOT / "assets" / "images" / "dad-fieldworks" / "canonical-yee"
MANIFEST_PATH = CANONICAL_DIR / "manifest.json"
INDEX_PATH = ROOT / "index.html"
README_PATH = ROOT / "README.md"
ASSET_INVENTORY_PATH = ROOT / "assets" / "asset_manifest.md"

SITE_TITLE = "DAD FieldWorks | Interactive Canonical-Yee Field Visualization"
SITE_DESCRIPTION = (
    "DAD FieldWorks visualizes precomputed Canonical-Yee PCB field data in an "
    "interactive native 3D workbench with X/Y/Z slices, saved frames and "
    "quantitative V/m scaling."
)
SECTION_HEADING = "Interactive Canonical-Yee Field Visualization"
COPYRIGHT_OWNER = "DigitalArtDeco Labs UG (haftungsbeschränkt)"

INTRO_PARAGRAPHS = (
    (
        "DAD FieldWorks loads precomputed Canonical-Yee field snapshots into its "
        "native wxWidgets and VTK engineering workbench. The Scientific Field View "
        "combines PCB geometry with a derived cell-centred electric-field magnitude "
        "in V/m and provides interactive X, Y and Z slice inspection, camera control, "
        "clipping and saved-frame navigation."
    ),
    (
        "The four views below show progressively later saved solver states on the "
        "same Z-oriented slice and with the same quantitative V/m color scale. This "
        "makes the spatial evolution of the electric-field magnitude along the "
        "microstrip structure directly comparable inside the 3D PCB geometry."
    ),
)

CAPABILITIES = (
    "Loads a precomputed Canonical-Yee result package through the normal Workbench user interface",
    "Displays PCB geometry and real stored field data together in 3D",
    "Shows derived cell-centred electric-field magnitude in V/m",
    "Provides selectable X, Y and Z field slices",
    "Presents five saved solver states with a common comparison scale",
    "Supports interactive camera, clipping, slice positioning and frame navigation",
    "Integrates a native Windows desktop interface using wxWidgets and VTK",
)

EXPECTED_SEQUENCE = (
    {
        "filename": "canonical-yee-z-slice-frame-02.png",
        "source": "canonical yee Z 11.PNG",
        "frame": 2,
        "step": 924,
        "width": 1440,
        "height": 861,
        "pixel_sha256": "88c0576bfe16916c2d6ce164aa806ab66312e80628874e29699dc4b8c5fa170f",
        "alt": "DAD FieldWorks Canonical-Yee electric-field magnitude, Z slice, saved frame 2 of 5, step 924.",
        "caption_title": "Frame 2/5: Step 924",
        "caption_body": (
            "An early saved field state showing the electric-field magnitude on the "
            "selected Z slice through the microstrip PCB geometry."
        ),
        "role": "Supporting sequence image — saved state 2/5",
    },
    {
        "filename": "canonical-yee-z-slice-frame-03.png",
        "source": "canonical yee Z 12.PNG",
        "frame": 3,
        "step": 1109,
        "width": 1440,
        "height": 862,
        "pixel_sha256": "414c9ed272bd2dff7d72462096c99e4eab2d559466386462e5d19a7e6f94f4f1",
        "alt": "DAD FieldWorks Canonical-Yee electric-field magnitude, Z slice, saved frame 3 of 5, step 1109.",
        "caption_title": "Frame 3/5: Step 1109",
        "caption_body": (
            "The field concentration develops along the trace while the geometry, "
            "slice position and quantitative V/m scale remain directly inspectable."
        ),
        "role": "Primary showcase and social-preview image — saved state 3/5",
    },
    {
        "filename": "canonical-yee-z-slice-frame-04.png",
        "source": "canonical yee Z 13.PNG",
        "frame": 4,
        "step": 1294,
        "width": 1439,
        "height": 861,
        "pixel_sha256": "9b96e8e040efeebe8859361c30b2d1c2cc0fb8d86d34b2bfac0a305629f7a8e0",
        "alt": "DAD FieldWorks Canonical-Yee electric-field magnitude, Z slice, saved frame 4 of 5, step 1294.",
        "caption_title": "Frame 4/5: Step 1294",
        "caption_body": (
            "A later saved state of the evolving electric-field distribution, "
            "displayed on the same common scale for visual comparison."
        ),
        "role": "Supporting sequence image — saved state 4/5",
    },
    {
        "filename": "canonical-yee-z-slice-frame-05.png",
        "source": "canonical yee Z 14.PNG",
        "frame": 5,
        "step": 4095,
        "width": 1440,
        "height": 863,
        "pixel_sha256": "5bcdb2394bfa9f80ec367074f691ef300c30a36676dd50e9549247013b4663c3",
        "alt": "DAD FieldWorks Canonical-Yee electric-field magnitude, Z slice, saved frame 5 of 5, step 4095.",
        "caption_title": "Frame 5/5: Step 4095",
        "caption_body": (
            "The final stored state in this sequence, showing the late-time spatial "
            "field distribution across the PCB structure."
        ),
        "role": "Supporting sequence image — saved state 5/5",
    },
)

EXPECTED_FILENAMES = tuple(item["filename"] for item in EXPECTED_SEQUENCE)
PRIMARY_FILENAME = EXPECTED_SEQUENCE[1]["filename"]
PRIMARY_URL = f"https://www.dadlabs.de/assets/images/dad-fieldworks/canonical-yee/{PRIMARY_FILENAME}"

SUPERSEDED_DIR = ROOT / "assets" / "screenshots" / "native_workbench_preview"

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".xml",
    ".yml",
    ".yaml",
}
SAFETY_SCAN_SUFFIXES = TEXT_SUFFIXES - {".py"}
PUBLIC_COPY_PATHS = (
    INDEX_PATH,
    README_PATH,
    ROOT / "docs" / "canonical_yee_field_visualization_provenance.md",
    MANIFEST_PATH,
)
PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)(?:(?<![a-z0-9+.-])[a-z]:[\\/]|file://|\\\\)[^\s<>'\"]+"
)
TRACKING_PATTERN = re.compile(
    r"(?i)(google-analytics|googletagmanager|gtag\s*\(|matomo|plausible\.io|"
    r"segment\.com|mixpanel|hotjar|dataLayer\s*=)"
)
TOKEN_PATTERN = re.compile(r"[a-z0-9_]+(?:-[a-z0-9_]+)*")

# Repository-private organization/customer identifiers are represented only by
# SHA-256 token digests so the validation source is safe to publish and scan.
EMPLOYER_CUSTOMER_TOKEN_DIGESTS = {
    "36aa04f4333ebc94260a496b27815226e288d9f946e5eca92362e42c09626290",
    "423d16ce8c066ceb5714dbb2f9d16eaa59e3571d0318367039755e7e64ceb32f",
}

REPEATED_NEGATIVE_PATTERNS = (
    re.compile(r"\bnot\s+production\s+ready\b", re.IGNORECASE),
    re.compile(r"\bnot\s+production\s+authorized\b", re.IGNORECASE),
    re.compile(r"\bnot\s+externally\s+validated\b", re.IGNORECASE),
    re.compile(r"\binternal\s+only\b", re.IGNORECASE),
    re.compile(r"\bprototype\s+only\b", re.IGNORECASE),
    re.compile(r"\bincomplete\s+product\b", re.IGNORECASE),
    re.compile(r"\blimitations?\b", re.IGNORECASE),
)
UNSUPPORTED_CLAIM_PATTERNS = (
    re.compile(r"\b(?:certified|certification)\b", re.IGNORECASE),
    re.compile(r"\bexternally\s+validated\b", re.IGNORECASE),
    re.compile(r"\bcommercial(?:ly)?\s+(?:available|availability)\b", re.IGNORECASE),
    re.compile(r"\b(?:production\s+(?:approved|approval|deployment)|approved\s+for\s+production)\b", re.IGNORECASE),
    re.compile(r"\bmeasur(?:ed|ement(?:-validated)?)\s+accuracy\b", re.IGNORECASE),
    re.compile(r"\b(?:complete|full)\s+s-?parameter\s+extraction\b", re.IGNORECASE),
    re.compile(r"\b(?:complete|full)\s+pcb\s+authoring\b", re.IGNORECASE),
    re.compile(r"\b(?:complete|full)\s+end-to-end\s+simulation\b", re.IGNORECASE),
)


def normalized(value: str) -> str:
    """Collapse human-readable text to a stable comparison form."""

    return " ".join(value.replace("\u00a0", " ").split())


class PageParser(HTMLParser):
    """Collect enough semantic structure to validate a static HTML page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.resources: list[tuple[str, str]] = []
        self.meta: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self.headings: list[str] = []
        self.title = ""
        self.workbench_text_parts: list[str] = []
        self.workbench_figures: list[dict[str, object]] = []

        self._section_stack: list[str | None] = []
        self._anchor_stack: list[dict[str, str | None]] = []
        self._figure_stack: list[dict[str, object]] = []
        self._caption_depth = 0
        self._heading_depth = 0
        self._heading_parts: list[str] = []
        self._title_depth = 0
        self._title_parts: list[str] = []

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str | None]:
        return {key.lower(): value for key, value in attrs}

    @property
    def inside_workbench(self) -> bool:
        return "workbench" in self._section_stack

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        data = self._attrs(attrs)
        if value := data.get("id"):
            self.ids.append(value)

        if tag == "section":
            self._section_stack.append(data.get("id"))
        elif tag == "a":
            self._anchor_stack.append(data)
            if href := data.get("href"):
                self.hrefs.append(href)
        elif tag == "figure":
            self._figure_stack.append(
                {
                    "inside_workbench": self.inside_workbench,
                    "classes": set((data.get("class") or "").split()),
                    "caption_parts": [],
                    "image": None,
                }
            )
        elif tag == "figcaption" and self._figure_stack:
            self._caption_depth += 1
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_depth += 1
            if self._heading_depth == 1:
                self._heading_parts = []
        elif tag == "title":
            self._title_depth += 1
            if self._title_depth == 1:
                self._title_parts = []

        if tag == "img":
            anchor = self._anchor_stack[-1] if self._anchor_stack else {}
            record = {
                "src": data.get("src"),
                "alt": data.get("alt"),
                "width": data.get("width"),
                "height": data.get("height"),
                "loading": data.get("loading"),
                "decoding": data.get("decoding"),
                "fetchpriority": data.get("fetchpriority"),
                "anchor_href": anchor.get("href"),
                "anchor_label": anchor.get("aria-label"),
            }
            self.images.append(record)
            if self._figure_stack:
                self._figure_stack[-1]["image"] = record
            if src := data.get("src"):
                self.resources.append(("img", src))
        elif tag == "script":
            if src := data.get("src"):
                self.resources.append(("script", src))
        elif tag in {"source", "video", "audio", "iframe"}:
            if src := data.get("src"):
                self.resources.append((tag, src))
        elif tag == "meta":
            self.meta.append(data)
        elif tag == "link":
            self.links.append(data)
            rel_tokens = set((data.get("rel") or "").lower().split())
            if rel_tokens & {"stylesheet", "icon", "preload", "modulepreload"}:
                if href := data.get("href"):
                    self.resources.append(("link", href))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "a" and self._anchor_stack:
            self._anchor_stack.pop()
        elif tag == "figcaption" and self._caption_depth:
            self._caption_depth -= 1
        elif tag == "figure" and self._figure_stack:
            figure = self._figure_stack.pop()
            if figure.get("inside_workbench"):
                self.workbench_figures.append(figure)
        elif tag == "section" and self._section_stack:
            self._section_stack.pop()
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading_depth:
            self._heading_depth -= 1
            if self._heading_depth == 0:
                self.headings.append(normalized(" ".join(self._heading_parts)))
        elif tag == "title" and self._title_depth:
            self._title_depth -= 1
            if self._title_depth == 0:
                self.title = normalized(" ".join(self._title_parts))

    def handle_data(self, data: str) -> None:
        if self.inside_workbench and data.strip():
            self.workbench_text_parts.append(data)
        if self._caption_depth and self._figure_stack and data.strip():
            caption_parts = self._figure_stack[-1]["caption_parts"]
            assert isinstance(caption_parts, list)
            caption_parts.append(data)
        if self._heading_depth and data.strip():
            self._heading_parts.append(data)
        if self._title_depth and data.strip():
            self._title_parts.append(data)


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def paeth_predictor(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def read_png(path: Path) -> dict[str, object]:
    """Validate a non-interlaced PNG and return structure plus pixel digest."""

    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("invalid PNG signature")

    offset = 8
    chunks: list[str] = []
    idat_parts: list[bytes] = []
    width = height = bit_depth = color_type = interlace = -1
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("truncated PNG chunk")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            raise ValueError("PNG chunk extends beyond end of file")
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        stored_crc = struct.unpack(">I", data[offset + 8 + length : chunk_end])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(chunk_data, actual_crc) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise ValueError(f"CRC mismatch in {chunk_type.decode('ascii', 'replace')}")
        name = chunk_type.decode("ascii")
        chunks.append(name)
        if name == "IHDR":
            if length != 13:
                raise ValueError("invalid IHDR length")
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
            if compression != 0 or filtering != 0:
                raise ValueError("unsupported PNG compression or filter method")
        elif name == "IDAT":
            idat_parts.append(chunk_data)
        offset = chunk_end
        if name == "IEND":
            break

    if offset != len(data):
        raise ValueError("trailing bytes after IEND")
    if chunks[:1] != ["IHDR"] or not idat_parts or chunks[-1:] != ["IEND"]:
        raise ValueError("missing or misplaced critical PNG chunks")
    if bit_depth != 8 or color_type not in {2, 6} or interlace != 0:
        raise ValueError(
            f"expected non-interlaced 8-bit RGB/RGBA, got depth={bit_depth}, "
            f"type={color_type}, interlace={interlace}"
        )

    bytes_per_pixel = 3 if color_type == 2 else 4
    stride = width * bytes_per_pixel
    inflated = zlib.decompress(b"".join(idat_parts))
    expected_inflated = height * (stride + 1)
    if len(inflated) != expected_inflated:
        raise ValueError(
            f"inflated data length {len(inflated)} != expected {expected_inflated}"
        )

    previous = bytearray(stride)
    pixels = bytearray()
    cursor = 0
    for _row_index in range(height):
        filter_type = inflated[cursor]
        cursor += 1
        scanline = inflated[cursor : cursor + stride]
        cursor += stride
        reconstructed = bytearray(stride)
        for column, encoded in enumerate(scanline):
            left = reconstructed[column - bytes_per_pixel] if column >= bytes_per_pixel else 0
            above = previous[column]
            upper_left = previous[column - bytes_per_pixel] if column >= bytes_per_pixel else 0
            if filter_type == 0:
                value = encoded
            elif filter_type == 1:
                value = (encoded + left) & 0xFF
            elif filter_type == 2:
                value = (encoded + above) & 0xFF
            elif filter_type == 3:
                value = (encoded + ((left + above) // 2)) & 0xFF
            elif filter_type == 4:
                value = (encoded + paeth_predictor(left, above, upper_left)) & 0xFF
            else:
                raise ValueError(f"invalid PNG filter type {filter_type}")
            reconstructed[column] = value
        pixels.extend(reconstructed)
        previous = reconstructed

    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "chunks": chunks,
        "pixel_sha256": hashlib.sha256(pixels).hexdigest(),
    }


def local_target_exists(source_file: Path, target: str) -> bool:
    parts = urlsplit(target)
    if parts.scheme or target.startswith(("//", "mailto:", "tel:")):
        return True
    if not parts.path:
        return True
    decoded = unquote(parts.path)
    candidate = (ROOT / decoded.lstrip("/")) if decoded.startswith("/") else (source_file.parent / decoded)
    candidate = candidate.resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return False
    return candidate.exists()


def iter_public_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] in {".git", ".local_temp", ".local_private_assets"}:
            continue
        if path.name == "CNAME" or path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return files


def parse_html(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def is_external(target: str) -> bool:
    parts = urlsplit(target)
    return parts.scheme.lower() in {"http", "https"} or target.startswith("//")


def staged_raw_incoming_paths() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    source_names = {str(item["source"]).casefold() for item in EXPECTED_SEQUENCE}
    paths = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    return [
        path
        for path in paths
        if path.startswith("_incoming/") or Path(path).name.casefold() in source_names
    ]


def validate_manifest_and_images(failures: list[str]) -> tuple[int, int, dict[str, str]]:
    metadata_chunk_count = 0
    published_count = 0
    actual_digests: dict[str, str] = {}

    if not MANIFEST_PATH.is_file():
        fail(failures, f"missing Canonical-Yee manifest: {MANIFEST_PATH.relative_to(ROOT)}")
        return published_count, metadata_chunk_count, actual_digests
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(failures, f"Canonical-Yee manifest is not valid UTF-8 JSON: {exc}")
        return published_count, metadata_chunk_count, actual_digests

    if not isinstance(manifest, dict):
        fail(failures, "Canonical-Yee manifest root must be an object")
        return published_count, metadata_chunk_count, actual_digests
    required_top = {"schema_id", "asset_set", "owner", "processing", "images"}
    missing_top = sorted(required_top - set(manifest))
    if missing_top:
        fail(failures, f"Canonical-Yee manifest missing top-level keys: {', '.join(missing_top)}")
    if manifest.get("schema_id") != "DAD_FIELDWORKS_CANONICAL_YEE_IMAGE_MANIFEST_V1":
        fail(failures, "Canonical-Yee manifest schema_id mismatch")
    if manifest.get("asset_set") != "Canonical-Yee Z-slice saved-frame sequence":
        fail(failures, "Canonical-Yee manifest asset_set mismatch")
    if manifest.get("owner") != COPYRIGHT_OWNER:
        fail(failures, "Canonical-Yee manifest copyright owner mismatch")
    processing = manifest.get("processing")
    if not isinstance(processing, dict):
        fail(failures, "Canonical-Yee manifest processing must be an object")
    else:
        if not normalized(str(processing.get("method") or "")):
            fail(failures, "Canonical-Yee manifest processing method is empty")
        expected_processing_flags = {
            "metadata_stripped": True,
            "decoded_pixels_preserved": True,
            "visual_edits": False,
        }
        for key, expected_value in expected_processing_flags.items():
            if processing.get(key) is not expected_value:
                fail(failures, f"Canonical-Yee manifest processing.{key} mismatch")
    assets = manifest.get("images")
    if not isinstance(assets, list):
        fail(failures, "Canonical-Yee manifest Assets must be an array")
        assets = []
    if len(assets) != 4:
        fail(failures, f"Canonical-Yee manifest must contain 4 assets, found {len(assets)}")

    records: dict[str, dict[str, object]] = {}
    manifest_order: list[str] = []
    primary_count = 0
    for index, record in enumerate(assets):
        if not isinstance(record, dict):
            fail(failures, f"Canonical-Yee manifest asset {index + 1} is not an object")
            continue
        required_record_keys = {
            "path",
            "source_filename",
            "sha256",
            "bytes",
            "width",
            "height",
            "description",
            "owner",
            "usage_role",
            "saved_state",
            "solver_step",
            "slice_axis",
            "quantity",
            "unit",
            "primary",
        }
        missing_record = sorted(required_record_keys - set(record))
        if missing_record:
            fail(
                failures,
                f"Canonical-Yee manifest asset {index + 1} missing keys: {', '.join(missing_record)}",
            )
        relative_value = record.get("path")
        filename = Path(str(relative_value or "")).name
        if not filename:
            fail(failures, f"Canonical-Yee manifest asset {index + 1} has no filename/path")
            continue
        if filename in records:
            fail(failures, f"duplicate Canonical-Yee manifest filename: {filename}")
        records[filename] = record
        manifest_order.append(filename)

    if tuple(manifest_order) != EXPECTED_FILENAMES:
        fail(failures, "Canonical-Yee manifest assets are not in chronological 2/5-to-5/5 order")
    if set(records) != set(EXPECTED_FILENAMES):
        fail(failures, "Canonical-Yee manifest filenames do not match the four normalized public filenames")

    for expected in EXPECTED_SEQUENCE:
        filename = str(expected["filename"])
        path = CANONICAL_DIR / filename
        record = records.get(filename, {})
        if not path.is_file():
            fail(failures, f"missing public Canonical-Yee screenshot: {path.relative_to(ROOT)}")
            continue
        published_count += 1
        try:
            png = read_png(path)
        except (OSError, ValueError, UnicodeError, zlib.error) as exc:
            fail(failures, f"{filename} is not a structurally valid PNG: {exc}")
            continue

        dimensions = (png["width"], png["height"])
        expected_dimensions = (expected["width"], expected["height"])
        if dimensions != expected_dimensions:
            fail(failures, f"{filename} dimensions {dimensions} != {expected_dimensions}")
        if png["pixel_sha256"] != expected["pixel_sha256"]:
            fail(failures, f"{filename} decoded pixels differ from the supplied screenshot")
        chunks = png["chunks"]
        assert isinstance(chunks, list)
        ancillary = [chunk for chunk in chunks if chunk not in {"IHDR", "IDAT", "IEND"}]
        metadata_chunk_count += len(ancillary)
        if ancillary:
            fail(failures, f"{filename} contains ancillary PNG chunks: {', '.join(ancillary)}")

        size = path.stat().st_size
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        actual_digests[filename] = digest
        relative = path.relative_to(ROOT).as_posix()
        if record.get("path") != relative:
            fail(failures, f"{filename} manifest public relative path mismatch")
        if record.get("source_filename") != expected["source"]:
            fail(failures, f"{filename} manifest source attachment filename mismatch")
        if record.get("sha256") != digest:
            fail(failures, f"{filename} manifest SHA-256 mismatch")
        if record.get("bytes") != size:
            fail(failures, f"{filename} manifest byte size mismatch")
        if (record.get("width"), record.get("height")) != dimensions:
            fail(failures, f"{filename} manifest dimensions mismatch")
        description = record.get("description")
        if not isinstance(description, str) or not normalized(description):
            fail(failures, f"{filename} manifest description is empty")
        if record.get("owner") != COPYRIGHT_OWNER:
            fail(failures, f"{filename} manifest copyright owner mismatch")
        role = record.get("usage_role")
        if not isinstance(role, str) or normalized(role).casefold() != str(expected["role"]).casefold():
            fail(failures, f"{filename} manifest usage role mismatch")
        if record.get("saved_state") != f"{expected['frame']}/5":
            fail(failures, f"{filename} manifest saved-frame mapping mismatch")
        if record.get("solver_step") != expected["step"]:
            fail(failures, f"{filename} manifest solver-step mapping mismatch")
        if record.get("slice_axis") != "Z":
            fail(failures, f"{filename} manifest slice axis must be Z")
        if record.get("quantity") != "Derived cell-centred electric-field magnitude":
            fail(failures, f"{filename} manifest quantity mismatch")
        if record.get("unit") != "V/m":
            fail(failures, f"{filename} manifest unit mismatch")
        if record.get("primary") is not (filename == PRIMARY_FILENAME):
            fail(failures, f"{filename} manifest primary flag mismatch")
        if record.get("primary") is True:
            primary_count += 1

    if primary_count != 1:
        fail(failures, f"Canonical-Yee manifest must mark exactly one primary image, found {primary_count}")

    return published_count, metadata_chunk_count, actual_digests


def validate_homepage(
    failures: list[str], actual_digests: dict[str, str]
) -> tuple[PageParser, int, int, int, bool]:
    if not INDEX_PATH.is_file():
        fail(failures, "missing index.html")
        return PageParser(), 0, 0, 0, False
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    parser = parse_html(INDEX_PATH)

    duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicates:
        fail(failures, f"duplicate HTML ids: {', '.join(duplicates)}")
    if "workbench" not in parser.ids:
        fail(failures, "index.html must preserve the workbench section anchor")
    if SECTION_HEADING not in parser.headings:
        fail(failures, f"index.html is missing the exact heading: {SECTION_HEADING}")
    if parser.title != SITE_TITLE:
        fail(failures, "HTML title does not match the Canonical-Yee page title")

    workbench_text = normalized(" ".join(parser.workbench_text_parts))
    for paragraph in INTRO_PARAGRAPHS:
        if normalized(paragraph) not in workbench_text:
            fail(failures, "Canonical-Yee section is missing one required capability paragraph")
    for capability in CAPABILITIES:
        if normalized(capability).casefold() not in workbench_text.casefold():
            fail(failures, f"Canonical-Yee capability summary is missing: {capability}")

    figures_by_filename: dict[str, dict[str, object]] = {}
    chronological_files: list[str] = []
    for figure in parser.workbench_figures:
        image = figure.get("image")
        if not isinstance(image, dict):
            continue
        src = str(image.get("src") or "")
        filename = Path(urlsplit(src).path).name
        if filename in EXPECTED_FILENAMES:
            chronological_files.append(filename)
            figures_by_filename[filename] = figure

    if tuple(chronological_files) != EXPECTED_FILENAMES:
        fail(failures, "homepage Canonical-Yee figures are not in chronological 2/5-to-5/5 order")
    if len(figures_by_filename) != 4:
        fail(failures, f"homepage must contain 4 distinct Canonical-Yee figures, found {len(figures_by_filename)}")

    missing_alt_count = 0
    accessibility_pass = True
    for expected in EXPECTED_SEQUENCE:
        filename = str(expected["filename"])
        figure = figures_by_filename.get(filename)
        if not figure:
            continue
        image = figure.get("image")
        assert isinstance(image, dict)
        expected_src = f"assets/images/dad-fieldworks/canonical-yee/{filename}"
        if image.get("src") != expected_src:
            fail(failures, f"{filename} homepage source path mismatch")
        if image.get("alt") != expected["alt"]:
            fail(failures, f"{filename} homepage alt text mismatch")
            missing_alt_count += 1
            accessibility_pass = False
        if image.get("width") != str(expected["width"]) or image.get("height") != str(expected["height"]):
            fail(failures, f"{filename} homepage width/height attributes mismatch")
        if image.get("decoding") != "async":
            fail(failures, f"{filename} must use decoding=async")
        if filename == PRIMARY_FILENAME:
            if image.get("loading") not in {None, "eager"}:
                fail(failures, f"primary image {filename} must not be lazy-loaded")
            if image.get("loading") == "eager" and image.get("fetchpriority") not in {None, "high"}:
                fail(failures, f"primary image {filename} has an unexpected fetch priority")
            classes = figure.get("classes")
            if not isinstance(classes, set) or "workbench-card-primary" not in classes:
                fail(failures, f"primary image {filename} must be the featured Workbench card")
        elif image.get("loading") != "lazy":
            fail(failures, f"supporting image {filename} must use loading=lazy")
        if image.get("anchor_href") != expected_src:
            fail(failures, f"{filename} must link to its full-resolution PNG")
            accessibility_pass = False
        if not normalized(str(image.get("anchor_label") or "")):
            # The image alt still gives the anchor an accessible name, but an
            # explicit action label is the established site convention.
            fail(failures, f"{filename} full-resolution link needs an aria-label")
            accessibility_pass = False
        caption_parts = figure.get("caption_parts")
        caption = normalized(" ".join(caption_parts if isinstance(caption_parts, list) else []))
        if normalized(str(expected["caption_title"])) not in caption or normalized(str(expected["caption_body"])) not in caption:
            fail(failures, f"{filename} homepage caption does not match its frame/step description")

    meta_lookup: dict[tuple[str, str], str | None] = {}
    for item in parser.meta:
        if item.get("property"):
            meta_lookup[("property", item["property"] or "")] = item.get("content")
        if item.get("name"):
            meta_lookup[("name", item["name"] or "")] = item.get("content")
    expected_meta = {
        ("name", "description"): SITE_DESCRIPTION,
        ("property", "og:type"): "website",
        ("property", "og:title"): SITE_TITLE,
        ("property", "og:description"): SITE_DESCRIPTION,
        ("property", "og:image"): PRIMARY_URL,
        ("property", "og:image:width"): str(EXPECTED_SEQUENCE[1]["width"]),
        ("property", "og:image:height"): str(EXPECTED_SEQUENCE[1]["height"]),
        ("property", "og:image:alt"): EXPECTED_SEQUENCE[1]["alt"],
        ("name", "twitter:card"): "summary_large_image",
        ("name", "twitter:title"): SITE_TITLE,
        ("name", "twitter:description"): SITE_DESCRIPTION,
        ("name", "twitter:image"): PRIMARY_URL,
        ("name", "twitter:image:alt"): EXPECTED_SEQUENCE[1]["alt"],
    }
    for key, expected in expected_meta.items():
        if meta_lookup.get(key) != expected:
            fail(failures, f"homepage metadata mismatch for {key[1]}")

    canonical = [
        item.get("href")
        for item in parser.links
        if "canonical" in set((item.get("rel") or "").lower().split())
    ]
    if canonical != ["https://www.dadlabs.de/"]:
        fail(failures, "canonical URL must be exactly https://www.dadlabs.de/")

    broken_images = 0
    for image in parser.images:
        src = str(image.get("src") or "")
        if not src or not local_target_exists(INDEX_PATH, src):
            broken_images += 1
            fail(failures, f"missing index.html image target: {src or '<empty>'}")
        if not normalized(str(image.get("alt") or "")):
            missing_alt_count += 1
            accessibility_pass = False
            fail(failures, f"index.html image has empty alt text: {src or '<empty>'}")

    broken_links = 0
    for href in parser.hrefs:
        if not local_target_exists(INDEX_PATH, href):
            broken_links += 1
            fail(failures, f"missing index.html link target: {href}")
        parts = urlsplit(href)
        if parts.fragment and not parts.scheme and not parts.path and parts.fragment not in parser.ids:
            broken_links += 1
            fail(failures, f"unresolved homepage fragment: #{parts.fragment}")

    external_assets = 0
    for kind, target in parser.resources:
        if is_external(target):
            external_assets += 1
            fail(failures, f"external {kind} dependency in index.html: {target}")
        elif not local_target_exists(INDEX_PATH, target):
            fail(failures, f"missing local {kind} dependency in index.html: {target}")

    if TRACKING_PATTERN.search(index_text):
        fail(failures, "tracking or analytics code appears in index.html")
    if "impressum.html" not in parser.hrefs or "datenschutz.html" not in parser.hrefs:
        fail(failures, "homepage must retain links to both legal pages")

    # The digest argument is used below in the inventory checks and retained in
    # this signature to keep homepage/manifest integration explicit.
    del actual_digests
    return parser, broken_images, broken_links, external_assets, accessibility_pass


def validate_readme_and_inventory(failures: list[str], actual_digests: dict[str, str]) -> None:
    if not README_PATH.is_file():
        fail(failures, "missing README.md")
        return
    readme_text = README_PATH.read_text(encoding="utf-8")
    if f"## {SECTION_HEADING}" not in readme_text:
        fail(failures, "README is missing the Canonical-Yee showcase heading")

    paths = [f"assets/images/dad-fieldworks/canonical-yee/{name}" for name in EXPECTED_FILENAMES]
    positions = [readme_text.find(path) for path in paths]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        fail(failures, "README Canonical-Yee sequence is missing or not chronological")
    for path in paths:
        if readme_text.count(path) < 2:
            fail(failures, f"README image is not clickable to its full-size asset: {path}")

    markdown_targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", readme_text)
    for target in markdown_targets:
        clean_target = target.strip().split(maxsplit=1)[0].strip("<>")
        if not local_target_exists(README_PATH, clean_target):
            fail(failures, f"missing README link/image target: {clean_target}")

    if not ASSET_INVENTORY_PATH.is_file():
        fail(failures, "missing assets/asset_manifest.md")
        return
    inventory_text = ASSET_INVENTORY_PATH.read_text(encoding="utf-8")
    for expected in EXPECTED_SEQUENCE:
        filename = str(expected["filename"])
        relative = f"assets/images/dad-fieldworks/canonical-yee/{filename}"
        digest = actual_digests.get(filename, "")
        if relative not in inventory_text:
            fail(failures, f"asset inventory is missing {relative}")
        # The machine-readable per-image manifest is the hash authority.  The
        # site-wide Markdown inventory must at least list all four public paths
        # and their owner without duplicating mutable hash data.
    if inventory_text.count(COPYRIGHT_OWNER) < 4:
        fail(failures, "asset inventory does not record the requested owner for all four images")


def validate_site_links_and_dependencies(failures: list[str]) -> tuple[int, int]:
    broken_links = 0
    external_assets = 0
    for html_path in sorted(ROOT.glob("*.html")):
        if html_path.resolve() == INDEX_PATH.resolve():
            continue
        parser = parse_html(html_path)
        for href in parser.hrefs:
            if not local_target_exists(html_path, href):
                broken_links += 1
                fail(failures, f"missing local link in {html_path.name}: {href}")
            parts = urlsplit(href)
            if parts.fragment and not parts.scheme:
                target_path = html_path if not parts.path else (html_path.parent / unquote(parts.path)).resolve()
                if target_path == html_path and parts.fragment not in parser.ids:
                    broken_links += 1
                    fail(failures, f"unresolved fragment in {html_path.name}: #{parts.fragment}")
        for kind, target in parser.resources:
            if is_external(target):
                external_assets += 1
                fail(failures, f"external {kind} dependency in {html_path.name}: {target}")
            elif not local_target_exists(html_path, target):
                fail(failures, f"missing local {kind} dependency in {html_path.name}: {target}")

    css_path = ROOT / "styles.css"
    if not css_path.is_file():
        fail(failures, "missing styles.css")
        return broken_links, external_assets
    css_text = css_path.read_text(encoding="utf-8")
    css_external = re.findall(r"(?i)(?:@import\s+|url\(\s*)['\"]?https?://", css_text)
    if css_external:
        external_assets += len(css_external)
        fail(failures, "external URL dependency appears in styles.css")
    for selector in (".workbench-gallery", ".workbench-card", ".workbench-card-primary"):
        if selector not in css_text:
            fail(failures, f"styles.css is missing Canonical-Yee gallery selector: {selector}")
    responsive_checks = (
        "@media" in css_text,
        bool(
            re.search(
                r"@media[^{}]*\{(?:(?!@media)[\s\S])*?\.workbench-gallery\s*\{[^}]*"
                r"grid-template-columns\s*:\s*(?:minmax\(0,\s*)?1fr",
                css_text,
            )
        ),
        bool(re.search(r"\.workbench-(?:card|image-link)\s+img\s*\{[^}]*width\s*:\s*100%", css_text, re.DOTALL)),
        "height: auto" in css_text,
    )
    if not all(responsive_checks):
        fail(failures, "styles.css lacks the required one-column/mobile aspect-ratio treatment")

    for js_path in sorted(ROOT.rglob("*.js")):
        if ".git" in js_path.parts:
            continue
        js_text = js_path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?i)(?:import\s*\(|from\s+|fetch\s*\(|new\s+Worker\s*\()\s*['\"]https?://", js_text):
            external_assets += 1
            fail(failures, f"external runtime dependency appears in {js_path.relative_to(ROOT)}")
        if TRACKING_PATTERN.search(js_text):
            fail(failures, f"tracking or analytics code appears in {js_path.relative_to(ROOT)}")
    return broken_links, external_assets


def validate_public_safety(failures: list[str]) -> tuple[int, int, int, int]:
    public_files = iter_public_text_files()
    absolute_private_path_count = 0
    employer_customer_count = 0
    for path in public_files:
        if path.name != "CNAME" and path.suffix.lower() not in SAFETY_SCAN_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = PRIVATE_PATH_PATTERN.findall(text)
        absolute_private_path_count += len(matches)
        tokens = TOKEN_PATTERN.findall(text.casefold())
        employer_customer_count += sum(
            hashlib.sha256(token.encode("utf-8")).hexdigest() in EMPLOYER_CUSTOMER_TOKEN_DIGESTS
            for token in tokens
        )
    if absolute_private_path_count:
        fail(failures, f"absolute Windows/UNC path count in public text: {absolute_private_path_count}")
    if employer_customer_count:
        fail(failures, f"private organization/customer token digest count: {employer_customer_count}")

    public_copy = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in PUBLIC_COPY_PATHS
        if path.is_file()
    )
    repeated_negative_count = sum(
        len(pattern.findall(public_copy)) for pattern in REPEATED_NEGATIVE_PATTERNS
    )
    unsupported_claim_count = sum(
        len(pattern.findall(public_copy)) for pattern in UNSUPPORTED_CLAIM_PATTERNS
    )
    if repeated_negative_count:
        fail(failures, f"repeated negative disclaimer count in showcase copy: {repeated_negative_count}")
    if unsupported_claim_count:
        fail(failures, f"unsupported positive claim count in showcase copy: {unsupported_claim_count}")
    return absolute_private_path_count, employer_customer_count, repeated_negative_count, unsupported_claim_count


def validate_superseded_content(failures: list[str]) -> int:
    remaining = 0
    if SUPERSEDED_DIR.exists():
        remaining += 1
        fail(failures, f"superseded screenshot directory remains: {SUPERSEDED_DIR.relative_to(ROOT)}")
    superseded_prefix = SUPERSEDED_DIR.relative_to(ROOT).as_posix()
    for path in iter_public_text_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        count = path.read_text(encoding="utf-8", errors="replace").count(superseded_prefix)
        if count:
            remaining += count
            fail(
                failures,
                f"superseded screenshot-directory reference remains in {path.relative_to(ROOT)}",
            )
    return remaining


def validate() -> tuple[list[str], dict[str, object]]:
    failures: list[str] = []
    published_count, metadata_chunk_count, actual_digests = validate_manifest_and_images(failures)
    parser, homepage_broken_images, homepage_broken_links, homepage_external_assets, accessibility_pass = validate_homepage(
        failures, actual_digests
    )
    validate_readme_and_inventory(failures, actual_digests)
    site_broken_links, site_external_assets = validate_site_links_and_dependencies(failures)
    private_path_count, employer_count, repeated_negative_count, unsupported_claim_count = validate_public_safety(failures)
    superseded_count = validate_superseded_content(failures)

    cname_path = ROOT / "CNAME"
    cname_exact = cname_path.is_file() and cname_path.read_bytes() == b"www.dadlabs.de\r\n"
    if not cname_exact:
        fail(failures, "CNAME bytes must remain exactly www.dadlabs.de followed by CRLF")
    legal_preserved = all((ROOT / name).is_file() for name in ("impressum.html", "datenschutz.html"))
    if not legal_preserved:
        fail(failures, "one or both required legal pages are missing")
    if not (ROOT / "assets" / "hero" / "pcb2d_microstrip_field_scientific_v2_hero.gif").is_file():
        fail(failures, "required unrelated hero animation is missing")

    try:
        raw_incoming = staged_raw_incoming_paths()
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        fail(failures, f"could not inspect staged paths: {exc}")
        raw_incoming = []
    if raw_incoming:
        fail(failures, f"raw incoming screenshot staged: {', '.join(raw_incoming)}")

    try:
        diff_check = subprocess.run(
            ["git", "diff", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if diff_check.returncode:
            fail(failures, "git diff --check failed")
    except (OSError, UnicodeError) as exc:
        fail(failures, f"could not run git diff --check: {exc}")

    chronological = tuple(
        Path(urlsplit(str((figure.get("image") or {}).get("src") or "")).path).name
        for figure in parser.workbench_figures
        if isinstance(figure.get("image"), dict)
        and Path(urlsplit(str((figure.get("image") or {}).get("src") or "")).path).name in EXPECTED_FILENAMES
    ) == EXPECTED_FILENAMES
    responsive_pass = not any("responsive" in item.lower() or "mobile" in item.lower() for item in failures)
    summary: dict[str, object] = {
        "NewCanonicalYeeScreenshotCount": published_count,
        "ChronologicalFrameSequenceQ": chronological,
        "PreviousFeaturedScreenshotSetRemovedQ": superseded_count == 0,
        "InteractiveCanonicalYeeCapabilityDescriptionUpdatedQ": SECTION_HEADING in parser.headings,
        "CapabilityFocusedPublicCopyQ": repeated_negative_count == 0 and unsupported_claim_count == 0,
        "RepeatedNegativeDisclaimerCount": repeated_negative_count,
        "UnsupportedClaimCount": unsupported_claim_count,
        "BrokenImageReferenceCount": homepage_broken_images,
        "BrokenLocalLinkCount": homepage_broken_links + site_broken_links,
        "ExternalAssetDependencyAddedCount": homepage_external_assets + site_external_assets,
        "PrivateRepositoryModifiedPathCount": private_path_count + employer_count,
        "CnameUnchangedQ": cname_exact,
        "LegalPagesPreservedQ": legal_preserved,
        "AccessibilityValidationPassQ": accessibility_pass,
        "ResponsiveLayoutValidationPassQ": responsive_pass,
        "AncillaryPngMetadataChunkCount": metadata_chunk_count,
        "RawIncomingAssetStagedCount": len(raw_incoming),
    }
    return failures, summary


def main() -> int:
    failures, summary = validate()
    print("DecisionClass: DadFieldWorksShowcaseCanonicalYeeFieldVisualizationSequencePublished")
    for key, value in summary.items():
        if isinstance(value, bool):
            value = "True" if value else "False"
        print(f"{key}: {value}")
    if failures:
        print("\nVALIDATION FAILED", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("ValidationPassQ: True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
