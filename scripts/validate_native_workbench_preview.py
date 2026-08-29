#!/usr/bin/env python3
"""Validate the current implemented-capability DAD FieldWorks showcase.

The validator is intentionally standard-library only and offline.  It checks
the four losslessly published screenshots, their manifest and chronological
presentation, the implemented-capability narrative, accessibility and
metadata requirements, local link integrity, and the bounded public-copy
contract requested for this publication tranche.
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
DOCS_INDEX_PATH = ROOT / "docs" / "README.md"
CURRENT_CAPABILITIES_PATH = ROOT / "docs" / "current_public_status.md"
CLAIM_BOUNDARIES_PATH = ROOT / "docs" / "claim_boundaries.md"
HERO_README_PATH = ROOT / "assets" / "hero" / "README.md"
EVIDENCE_ARCHITECTURE_PATH = ROOT / "docs" / "evidence_contract_architecture.md"

SITE_TITLE = "DAD FieldWorks | Native Electromagnetic Engineering Workbench"
SITE_DESCRIPTION = (
    "DAD FieldWorks combines a native True-3D Yee FDTD core, scientific field "
    "visualization, RF result processing and evidence-bound engineering in an "
    "integrated desktop Workbench."
)
SOCIAL_DESCRIPTION = (
    "Native True-3D Yee FDTD, scientific field visualization, RF result "
    "processing and evidence-bound engineering in one desktop Workbench."
)
HERO_HEADLINE = "Physics-Based Electromagnetic Engineering for PCB and RF Design"
HERO_TAGLINE = SITE_DESCRIPTION
CAPABILITY_SECTION_HEADING = (
    "Implemented foundations for native fields, scientific views and engineering results."
)
CAPABILITY_SECTION_PARAGRAPH = (
    "The current implementation combines full-vector time-domain computation, "
    "scientific visualization and structured RF processing. Each capability is "
    "presented at the scope supported by current code, focused tests or an "
    "internally exercised reference case."
)
WORKBENCH_SECTION_HEADING = "Canonical-Yee Field Visualization in the Native Workbench"
README_WORKBENCH_HEADING = "Canonical-Yee Field Visualization"
COPYRIGHT_OWNER = "DigitalArtDeco Labs UG (haftungsbeschränkt)"
README_PRODUCT_PARAGRAPH = (
    "DAD FieldWorks combines a DAD-owned full-vector 3D Yee FDTD core, scientific "
    "field visualization, RF result processing and evidence-bound engineering in "
    "an integrated native desktop Workbench."
)
CURRENT_CAPABILITIES_INTRO = (
    "DAD FieldWorks is developed by DigitalArtDeco Labs UG (haftungsbeschränkt). "
    "The current public presentation is based on implemented code, focused tests "
    "and internally exercised engineering reference cases."
)

HERO_PROOF_ITEMS = (
    "Full-vector Yee fields",
    "Native field visualization",
    "Port V/I acquisition",
    "Direct DFT and pseudowaves",
    "Matrix, Cartesian and Smith views",
    "Hash-bound experiment provenance",
)

CAPABILITY_HEADINGS = (
    "Native True-3D Electromagnetic Simulation",
    "Scientific Field Visualization",
    "Port Signals and RF Processing",
    "S-Parameter Result Workbench",
    "Quasi-TEM Cross-Section Analysis",
    "Evidence-Bound Engineering",
    "Native Engineering Workbench",
)

CAPABILITY_STATUS_LABELS = (
    "Implemented and internally exercised",
    "Scientific visualization implemented",
    "RF core implemented",
    "Result Workbench implemented",
    "Internal numerical foundation implemented",
    "Evidence architecture implemented",
    "Native desktop architecture implemented",
)

CAPABILITY_REQUIRED_COPY = (
    (
        "DAD FieldWorks contains a DAD-owned full-vector 3D time-domain "
        "electromagnetic core based on the spatially staggered Yee method. Ex, Ey, "
        "Ez, Hx, Hy and Hz are represented at their native lattice positions and "
        "advanced through explicit leapfrog updates."
    ),
    (
        "The native Workbench embeds VTK inside its wxWidgets desktop interface. "
        "Its scientific view combines DAD-owned PCB geometry with field datasets "
        "and supports component-native signed scalar slices, derived collocated "
        "vector magnitude, vector glyphs, magnitude isosurfaces, engineering units, "
        "axes, camera controls, clipping, picking and explicit frame selection."
    ),
    (
        "DAD FieldWorks records port voltage from native electric-field paths and "
        "current from native magnetic-field contours. Its downstream RF core "
        "provides Yee-aware temporal alignment, deterministic direct Fourier "
        "transformation, real-reference power-normalized pseudowaves and structured "
        "one-port and two-port processing."
    ),
    (
        "The native Result Workbench presents versioned complex S-parameter "
        "datasets through Matrix, Cartesian and Smith-chart views. The Matrix view "
        "exposes response and excitation entries at a selected frequency. Cartesian "
        "views provide selectable complex traces and exact markers. The Smith-chart "
        "view presents diagonal reflection traces with gamma and normalized-impedance "
        "readout."
    ),
    (
        "DAD FieldWorks implements evidence-bound C++ foundations for lossless "
        "two-conductor quasi-TEM cross-section analysis. Paired electrostatic and "
        "vacuum-companion magnetic formulations record iterations, residuals, "
        "convergence thresholds and finite-value checks."
    ),
    (
        "Every controlled computation is treated as a traceable engineering "
        "experiment. DAD FieldWorks binds model inputs, solver identity, executable "
        "state, execution context, numerical payloads and evaluation results into a "
        "versioned evidence chain."
    ),
    (
        "DAD FieldWorks uses wxWidgets for its native desktop shell, DAD-owned "
        "engineering models and a dedicated PCB canvas. VTK provides the scientific "
        "visualization backend. Project, solver, result and presentation contracts "
        "remain explicitly separated so the computational core stays independent "
        "from the desktop presentation layer."
    ),
)

WORKBENCH_INTRO_PARAGRAPHS = (
    (
        "A five-state Canonical-Yee reference package has been exercised internally "
        "for magnitude, slice, camera and saved-frame inspection in the native GUI. "
        "The Scientific Field View combines PCB geometry with derived cell-centred "
        "electric-field magnitude in V/m while retaining the native full-vector "
        "field package as its source."
    ),
    (
        "The four published captures show progressively later saved states on the "
        "same Z-oriented slice and with the same quantitative V/m color scale. Their "
        "fixed geometry and scale make the spatial field evolution along the "
        "microstrip directly comparable."
    ),
)

WORKBENCH_CAPABILITIES = (
    "Five saved full-vector field states from one internally exercised PCB reference run.",
    "PCB geometry and stored field data presented together in a native 3D view.",
    "Derived cell-centred electric-field magnitude with quantitative V/m units.",
    "Selectable X, Y and Z slices with explicit source placement.",
    "Camera, clipping, slice positioning and deterministic frame navigation.",
    "Native Windows desktop integration using wxWidgets and VTK.",
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
ACTIVE_PRESENTATION_PATHS = (
    INDEX_PATH,
    README_PATH,
    DOCS_INDEX_PATH,
    CURRENT_CAPABILITIES_PATH,
    CLAIM_BOUNDARIES_PATH,
    HERO_README_PATH,
)
CLAIM_COPY_PATHS = ACTIVE_PRESENTATION_PATHS + (
    ROOT / "docs" / "canonical_yee_field_visualization_provenance.md",
    MANIFEST_PATH,
)
UNSUPPORTED_CLAIM_COPY_PATHS = (
    INDEX_PATH,
    README_PATH,
    CURRENT_CAPABILITIES_PATH,
    HERO_README_PATH,
    ROOT / "docs" / "canonical_yee_field_visualization_provenance.md",
)
PUBLIC_LINK_SURFACE_PATHS = ACTIVE_PRESENTATION_PATHS + (EVIDENCE_ARCHITECTURE_PATH,)
PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)(?:(?<![a-z0-9+.-])[a-z]:[\\/]|file://|\\\\)[^\s<>'\"]+"
)
TRACKING_PATTERN = re.compile(
    r"(?i)(google-analytics|googletagmanager|gtag\s*\(|matomo|plausible\.io|"
    r"segment\.com|mixpanel|hotjar|dataLayer\s*=)"
)
PRIVATE_COMMIT_HASH_PATTERN = re.compile(r"(?i)\b[0-9a-f]{40}\b")
PRIVATE_CONTEXT_PATTERN = re.compile(
    r"(?i)\b(?:customer|employer|employee)(?:[_ -](?:name|id|metadata))?\b|"
    r"\breferences[_-]local\b"
)
INTERNAL_IDENTIFIER_PREFIXES = (
    "request",
    "attempt",
    "authority",
    "decision",
    "failure",
    "process",
)
INTERNAL_IDENTIFIER_PATTERN = re.compile(
    r"(?i)\b(?:" + "|".join(INTERNAL_IDENTIFIER_PREFIXES) + r")[_ -]?(?:id|class)\b"
)
ROADMAP_LINK_PATTERN = re.compile(
    r"(?i)(?:href\s*=\s*['\"][^'\"]*roadmap[^'\"]*['\"]|"
    r"\[[^\]]*\]\([^)]*roadmap[^)]*\)|#roadmap\b)"
)
LIMITATIONS_HEADING_PATTERN = re.compile(
    r"(?i)\b(?:limitations?|missing\s+features?|current\s+blockers?|"
    r"not\s+yet\s+implemented)\b"
)
MATHEMATICA_PRODUCT_PATTERN = re.compile(r"(?i)\b(?:mathematica|wolfram)\b")
SCIENTIFIC_IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}

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
    re.compile(r"\bcommercial(?:ly)?\s+validated\b", re.IGNORECASE),
    re.compile(r"\bindustry\s+validated\b", re.IGNORECASE),
    re.compile(r"\bmeasurement[- ]validated\b", re.IGNORECASE),
    re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
    re.compile(r"\b(?:production\s+(?:approved|approval|deployment)|approved\s+for\s+production)\b", re.IGNORECASE),
    re.compile(r"\bmeasur(?:ed|ement(?:-validated)?)\s+accuracy\b", re.IGNORECASE),
    re.compile(r"\b(?:a\s+)?(?:complete|full)\s+(?:replacement\s+for\s+)?(?:hfss|cst|comsol)\b", re.IGNORECASE),
    re.compile(r"\b(?:hfss|cst|comsol)\s+replacement\b", re.IGNORECASE),
    re.compile(r"\bcomplete\s+arbitrary[- ]pcb\s+s-?parameter\s+solver\b", re.IGNORECASE),
    re.compile(r"\bcomplete\s+broadband\s+modal[- ]port\b", re.IGNORECASE),
    re.compile(r"\bcomplete\s+real\s+s[- ]matrix\s+from\s+arbitrary\s+3d\s+geometry\b", re.IGNORECASE),
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
        self.heading_records: list[tuple[str, str, str | None]] = []
        self.title = ""
        self.all_text_parts: list[str] = []
        self.section_text_parts: dict[str, list[str]] = {}
        self.workbench_text_parts: list[str] = []
        self.workbench_figures: list[dict[str, object]] = []

        self._section_stack: list[str | None] = []
        self._anchor_stack: list[dict[str, str | None]] = []
        self._figure_stack: list[dict[str, object]] = []
        self._caption_depth = 0
        self._heading_depth = 0
        self._heading_parts: list[str] = []
        self._heading_tag = ""
        self._heading_section: str | None = None
        self._title_depth = 0
        self._title_parts: list[str] = []
        self._suppressed_text_depth = 0

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str | None]:
        return {key.lower(): value for key, value in attrs}

    @property
    def inside_workbench(self) -> bool:
        return "workbench" in self._section_stack

    def section_text(self, section_id: str) -> str:
        return normalized(" ".join(self.section_text_parts.get(section_id, [])))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        data = self._attrs(attrs)
        if tag in {"script", "style"}:
            self._suppressed_text_depth += 1
        if value := data.get("id"):
            self.ids.append(value)

        if tag == "section":
            section_key = data.get("id") or data.get("aria-labelledby")
            self._section_stack.append(section_key)
            if section_key:
                self.section_text_parts.setdefault(section_key, [])
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
                self._heading_tag = tag
                self._heading_section = next(
                    (section for section in reversed(self._section_stack) if section),
                    None,
                )
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
        if tag in {"script", "style"}:
            self._suppressed_text_depth = max(0, self._suppressed_text_depth - 1)
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
                heading = normalized(" ".join(self._heading_parts))
                self.headings.append(heading)
                self.heading_records.append(
                    (self._heading_tag, heading, self._heading_section)
                )
        elif tag == "title" and self._title_depth:
            self._title_depth -= 1
            if self._title_depth == 0:
                self.title = normalized(" ".join(self._title_parts))

    def handle_data(self, data: str) -> None:
        if not self._suppressed_text_depth and data.strip():
            self.all_text_parts.append(data)
            for section in self._section_stack:
                if section:
                    self.section_text_parts.setdefault(section, []).append(data)
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


def added_scientific_image_paths() -> list[str]:
    diff_result = subprocess.run(
        ["git", "diff", "HEAD", "--name-only", "--diff-filter=A", "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    untracked_result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    paths = {
        line.strip().replace("\\", "/")
        for output in (diff_result.stdout, untracked_result.stdout)
        for line in output.splitlines()
        if line.strip()
    }
    return sorted(
        path
        for path in paths
        if path.startswith("assets/")
        and Path(path).suffix.casefold() in SCIENTIFIC_IMAGE_SUFFIXES
    )


def validate_manifest_and_images(failures: list[str]) -> tuple[int, int, dict[str, str]]:
    metadata_chunk_count = 0
    published_count = 0
    actual_digests: dict[str, str] = {}

    actual_canonical_png_names = tuple(
        sorted(path.name for path in CANONICAL_DIR.glob("*.png") if path.is_file())
    )
    if actual_canonical_png_names != tuple(sorted(EXPECTED_FILENAMES)):
        fail(
            failures,
            "Canonical-Yee directory must contain exactly the four approved PNG files",
        )

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
) -> tuple[PageParser, int, int, int, bool, bool, int]:
    if not INDEX_PATH.is_file():
        fail(failures, "missing index.html")
        return PageParser(), 0, 0, 0, False, False, 0
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    parser = parse_html(INDEX_PATH)

    duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicates:
        fail(failures, f"duplicate HTML ids: {', '.join(duplicates)}")
    if "workbench" not in parser.ids:
        fail(failures, "index.html must preserve the workbench section anchor")
    required_section_ids = {
        "capabilities",
        "workbench",
        "evidence",
        "architecture",
        "about",
        "materials",
        "contact",
    }
    missing_section_ids = sorted(required_section_ids - set(parser.ids))
    if missing_section_ids:
        fail(failures, f"index.html is missing section anchors: {', '.join(missing_section_ids)}")
    if parser.title != SITE_TITLE:
        fail(failures, "HTML title does not match the current Workbench page title")

    hero_headings = tuple(
        heading
        for tag, heading, section in parser.heading_records
        if tag == "h1" and section == "hero-title"
    )
    hero_text = parser.section_text("hero-title")
    hero_checks = (
        hero_headings == (HERO_HEADLINE,),
        normalized(HERO_TAGLINE) in hero_text,
        all(normalized(item) in hero_text for item in HERO_PROOF_ITEMS),
        bool(
            re.search(
                r"<ul\b[^>]*\bclass\s*=\s*['\"][^'\"]*\bcapability-strip\b[^'\"]*['\"]",
                index_text,
                re.IGNORECASE,
            )
        ),
    )
    if not hero_checks[0]:
        fail(failures, "homepage hero must contain the exact current capability headline")
    if not hero_checks[1]:
        fail(failures, "homepage hero must contain the exact current capability tagline")
    if not hero_checks[2]:
        fail(failures, "homepage hero proof strip is missing one or more required items")
    if not hero_checks[3]:
        fail(failures, "homepage hero is missing the semantic capability proof strip")

    capability_headings = tuple(
        heading
        for tag, heading, section in parser.heading_records
        if tag == "h3" and section == "capabilities"
    )
    capability_text = parser.section_text("capabilities")
    capability_checks = (
        CAPABILITY_SECTION_HEADING in parser.headings,
        normalized(CAPABILITY_SECTION_PARAGRAPH) in capability_text,
        capability_headings == CAPABILITY_HEADINGS,
        all(normalized(label) in capability_text for label in CAPABILITY_STATUS_LABELS),
        all(normalized(paragraph) in capability_text for paragraph in CAPABILITY_REQUIRED_COPY),
        all(metric in capability_text for metric in ("4,096", "5", "2 × 4,096 samples")),
    )
    if not capability_checks[0]:
        fail(failures, "homepage is missing the exact implemented-capability section heading")
    if not capability_checks[1]:
        fail(failures, "implemented-capability section is missing its scope paragraph")
    if not capability_checks[2]:
        fail(failures, "homepage capability-card headings do not match the seven approved groups")
    if not capability_checks[3]:
        fail(failures, "homepage capability cards are missing one or more scope labels")
    if not capability_checks[4]:
        fail(failures, "homepage capability cards are missing required implemented-capability copy")
    if not capability_checks[5]:
        fail(failures, "homepage reference-case metrics are incomplete")

    presentation_pass = all(hero_checks) and all(capability_checks)

    workbench_text = normalized(" ".join(parser.workbench_text_parts))
    if WORKBENCH_SECTION_HEADING not in parser.headings:
        fail(failures, f"index.html is missing the exact heading: {WORKBENCH_SECTION_HEADING}")
    for paragraph in WORKBENCH_INTRO_PARAGRAPHS:
        if normalized(paragraph) not in workbench_text:
            fail(failures, "Canonical-Yee section is missing one required capability paragraph")
    for capability in WORKBENCH_CAPABILITIES:
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
        ("property", "og:description"): SOCIAL_DESCRIPTION,
        ("property", "og:image"): PRIMARY_URL,
        ("property", "og:image:width"): str(EXPECTED_SEQUENCE[1]["width"]),
        ("property", "og:image:height"): str(EXPECTED_SEQUENCE[1]["height"]),
        ("property", "og:image:alt"): EXPECTED_SEQUENCE[1]["alt"],
        ("name", "twitter:card"): "summary_large_image",
        ("name", "twitter:title"): SITE_TITLE,
        ("name", "twitter:description"): SOCIAL_DESCRIPTION,
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
    approved_image_sources = {
        f"assets/images/dad-fieldworks/canonical-yee/{filename}"
        for filename in EXPECTED_FILENAMES
    }
    unexpected_scientific_images: set[str] = set()
    for image in parser.images:
        src = str(image.get("src") or "")
        if not src or not local_target_exists(INDEX_PATH, src):
            broken_images += 1
            fail(failures, f"missing index.html image target: {src or '<empty>'}")
        parts = urlsplit(src)
        normalized_src = unquote(parts.path).lstrip("/").replace("\\", "/")
        if (
            normalized_src
            and not parts.scheme
            and Path(normalized_src).suffix.casefold() in SCIENTIFIC_IMAGE_SUFFIXES
            and normalized_src not in approved_image_sources
        ):
            unexpected_scientific_images.add(normalized_src)
        if not normalized(str(image.get("alt") or "")):
            missing_alt_count += 1
            accessibility_pass = False
            fail(failures, f"index.html image has empty alt text: {src or '<empty>'}")
    if unexpected_scientific_images:
        fail(
            failures,
            "homepage references an image outside the four approved Canonical-Yee assets: "
            + ", ".join(sorted(unexpected_scientific_images)),
        )

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
    return (
        parser,
        broken_images,
        broken_links,
        external_assets,
        accessibility_pass,
        presentation_pass,
        len(unexpected_scientific_images),
    )


def markdown_headings(text: str, level: int) -> tuple[str, ...]:
    marker = "#" * level
    return tuple(
        normalized(match)
        for match in re.findall(rf"(?m)^{re.escape(marker)}\s+(.+?)\s*$", text)
    )


def validate_readme_and_inventory(
    failures: list[str], actual_digests: dict[str, str]
) -> bool:
    if not README_PATH.is_file():
        fail(failures, "missing README.md")
        return False
    readme_text = README_PATH.read_text(encoding="utf-8")
    level_two_headings = markdown_headings(readme_text, 2)
    level_three_headings = markdown_headings(readme_text, 3)
    readme_checks = (
        "Implemented Engineering Capabilities" in level_two_headings,
        README_WORKBENCH_HEADING in level_two_headings,
        level_three_headings == CAPABILITY_HEADINGS,
        normalized(README_PRODUCT_PARAGRAPH) in normalized(readme_text),
    )
    if not readme_checks[0]:
        fail(failures, "README is missing the implemented-capability heading")
    if not readme_checks[1]:
        fail(failures, "README is missing the Canonical-Yee showcase heading")
    if not readme_checks[2]:
        fail(failures, "README capability headings do not match the seven approved groups")
    if not readme_checks[3]:
        fail(failures, "README is missing the current product capability paragraph")

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
        return False
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
    return all(readme_checks)


def validate_current_capability_docs(failures: list[str]) -> bool:
    checks: list[bool] = []
    if not CURRENT_CAPABILITIES_PATH.is_file():
        fail(failures, "missing docs/current_public_status.md")
        checks.append(False)
    else:
        current_text = CURRENT_CAPABILITIES_PATH.read_text(encoding="utf-8")
        current_h1 = markdown_headings(current_text, 1)
        current_h2 = markdown_headings(current_text, 2)
        current_checks = (
            current_h1 == ("Current Implemented Capabilities",),
            current_h2 == CAPABILITY_HEADINGS,
            normalized(CURRENT_CAPABILITIES_INTRO) in normalized(current_text),
        )
        checks.extend(current_checks)
        if not current_checks[0]:
            fail(failures, "current capability document has an unexpected title")
        if not current_checks[1]:
            fail(failures, "current capability document does not contain the seven approved groups")
        if not current_checks[2]:
            fail(failures, "current capability document is missing its evidence-scope introduction")

    if not DOCS_INDEX_PATH.is_file():
        fail(failures, "missing docs/README.md")
        checks.append(False)
    else:
        docs_index_text = DOCS_INDEX_PATH.read_text(encoding="utf-8")
        docs_index_checks = (
            "[Current implemented capabilities](current_public_status.md)" in docs_index_text,
            "[Claim boundaries](claim_boundaries.md)" in docs_index_text,
        )
        checks.extend(docs_index_checks)
        if not all(docs_index_checks):
            fail(failures, "documentation index is missing current capability references")

    if not CLAIM_BOUNDARIES_PATH.is_file():
        fail(failures, "missing docs/claim_boundaries.md")
        checks.append(False)
    else:
        claim_text = CLAIM_BOUNDARIES_PATH.read_text(encoding="utf-8")
        claim_checks = (
            "## Supported Capability Scope" in claim_text,
            "## Internally Exercised Reference Scope" in claim_text,
            "## Publication Rule" in claim_text,
            all(
                term in claim_text
                for term in (
                    "full-vector 3D time-domain electromagnetic core",
                    "Yee-aware temporal alignment",
                    "S-parameter model",
                    "wxWidgets desktop integration",
                    "quasi-TEM cross-section foundations",
                    "immutable evidence packages",
                )
            ),
        )
        checks.extend(claim_checks)
        if not all(claim_checks):
            fail(failures, "claim-boundary document is missing current capability scope")

    return bool(checks) and all(checks)


def validate_site_links_and_dependencies(failures: list[str]) -> tuple[int, int, int]:
    broken_links = 0
    broken_images = 0
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
                if kind == "img":
                    broken_images += 1
                fail(failures, f"missing local {kind} dependency in {html_path.name}: {target}")

    css_path = ROOT / "styles.css"
    if not css_path.is_file():
        fail(failures, "missing styles.css")
        return broken_links, broken_images, external_assets
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
    return broken_links, broken_images, external_assets


def read_existing_text(paths: tuple[Path, ...]) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in paths
        if path.is_file()
    )


def validate_public_safety(failures: list[str]) -> dict[str, int | bool]:
    public_files = iter_public_text_files()
    absolute_private_path_count = 0
    internal_identifier_count = 0
    private_context_count = 0
    for path in public_files:
        if path.name != "CNAME" and path.suffix.lower() not in SAFETY_SCAN_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        absolute_private_path_count += len(PRIVATE_PATH_PATTERN.findall(text))
        internal_identifier_count += len(INTERNAL_IDENTIFIER_PATTERN.findall(text))
        private_context_count += len(PRIVATE_CONTEXT_PATTERN.findall(text))
    if absolute_private_path_count:
        fail(failures, f"absolute Windows/UNC path count in public text: {absolute_private_path_count}")
    if internal_identifier_count:
        fail(failures, f"internal identifier count in public text: {internal_identifier_count}")
    if private_context_count:
        fail(failures, f"private personnel/customer context count in public text: {private_context_count}")

    public_copy = read_existing_text(CLAIM_COPY_PATHS)
    claim_assertion_copy = read_existing_text(UNSUPPORTED_CLAIM_COPY_PATHS)
    active_copy = read_existing_text(ACTIVE_PRESENTATION_PATHS)
    public_link_copy = read_existing_text(PUBLIC_LINK_SURFACE_PATHS)
    repeated_negative_count = sum(
        len(pattern.findall(public_copy)) for pattern in REPEATED_NEGATIVE_PATTERNS
    )
    unsupported_claim_count = sum(
        len(pattern.findall(claim_assertion_copy)) for pattern in UNSUPPORTED_CLAIM_PATTERNS
    )
    en_dash_count = active_copy.count("\u2013") + len(
        re.findall(r"&ndash;", active_copy, re.IGNORECASE)
    )
    em_dash_count = active_copy.count("\u2014") + len(
        re.findall(r"&mdash;", active_copy, re.IGNORECASE)
    )
    roadmap_link_count = len(ROADMAP_LINK_PATTERN.findall(public_link_copy))
    mathematica_product_path_count = len(MATHEMATICA_PRODUCT_PATTERN.findall(active_copy))
    private_commit_hash_count = len(PRIVATE_COMMIT_HASH_PATTERN.findall(active_copy))

    presentation_headings: list[str] = []
    if INDEX_PATH.is_file():
        presentation_headings.extend(parse_html(INDEX_PATH).headings)
    for path in ACTIVE_PRESENTATION_PATHS:
        if path.suffix.casefold() == ".md" and path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            presentation_headings.extend(
                normalized(item)
                for item in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", text)
            )
    limitations_heading_count = sum(
        bool(LIMITATIONS_HEADING_PATTERN.search(heading))
        for heading in presentation_headings
    )

    if repeated_negative_count:
        fail(failures, f"repeated negative disclaimer count in showcase copy: {repeated_negative_count}")
    if unsupported_claim_count:
        fail(failures, f"unsupported positive claim count in showcase copy: {unsupported_claim_count}")
    if en_dash_count:
        fail(failures, f"AI-style en dash count in current public presentation: {en_dash_count}")
    if em_dash_count:
        fail(failures, f"AI-style em dash count in current public presentation: {em_dash_count}")
    if roadmap_link_count:
        fail(failures, f"public roadmap link count in current publication surface: {roadmap_link_count}")
    if limitations_heading_count:
        fail(failures, f"public limitations/missing-features heading count: {limitations_heading_count}")
    if mathematica_product_path_count:
        fail(failures, f"Mathematica/Wolfram product-path claim count: {mathematica_product_path_count}")
    if private_commit_hash_count:
        fail(failures, f"private commit-like hash count in current public copy: {private_commit_hash_count}")

    return {
        "absolute_private_path_count": absolute_private_path_count,
        "internal_identifier_count": internal_identifier_count,
        "private_context_count": private_context_count,
        "private_commit_hash_count": private_commit_hash_count,
        "repeated_negative_count": repeated_negative_count,
        "unsupported_claim_count": unsupported_claim_count,
        "en_dash_count": en_dash_count,
        "em_dash_count": em_dash_count,
        "roadmap_link_count": roadmap_link_count,
        "limitations_heading_count": limitations_heading_count,
        "mathematica_product_path_count": mathematica_product_path_count,
    }


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
    (
        parser,
        homepage_broken_images,
        homepage_broken_links,
        homepage_external_assets,
        accessibility_pass,
        homepage_presentation_pass,
        unexpected_homepage_image_count,
    ) = validate_homepage(failures, actual_digests)
    readme_presentation_pass = validate_readme_and_inventory(failures, actual_digests)
    docs_presentation_pass = validate_current_capability_docs(failures)
    site_broken_links, site_broken_images, site_external_assets = validate_site_links_and_dependencies(failures)
    safety = validate_public_safety(failures)
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
        added_scientific_images = added_scientific_image_paths()
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        fail(failures, f"could not inspect newly added public image paths: {exc}")
        added_scientific_images = []
    if added_scientific_images:
        fail(
            failures,
            "new scientific/decorative image assets were added in this update: "
            + ", ".join(added_scientific_images),
        )

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
    current_presentation_pass = (
        homepage_presentation_pass
        and readme_presentation_pass
        and docs_presentation_pass
    )
    only_implemented_capabilities = (
        current_presentation_pass
        and safety["unsupported_claim_count"] == 0
        and safety["repeated_negative_count"] == 0
        and safety["limitations_heading_count"] == 0
        and safety["roadmap_link_count"] == 0
    )
    fabricated_scientific_image_count = (
        unexpected_homepage_image_count + len(added_scientific_images)
    )
    broken_image_count = homepage_broken_images + site_broken_images
    broken_internal_link_count = homepage_broken_links + site_broken_links
    private_copy_indicator_count = (
        safety["absolute_private_path_count"]
        + safety["internal_identifier_count"]
        + safety["private_context_count"]
        + safety["private_commit_hash_count"]
    )
    summary: dict[str, object] = {
        "PublicShowcaseCurrentCapabilityPresentationUpdatedQ": current_presentation_pass,
        "OnlyImplementedCapabilitiesPresentedQ": only_implemented_capabilities,
        "UnsupportedCapabilityClaimCount": safety["unsupported_claim_count"],
        "PublicLimitationsSectionAddedQ": safety["limitations_heading_count"] > 0,
        "PrivateRepositoryMutationCount": "ExternalReadOnlyVerificationRequired",
        "FabricatedScientificImageCount": fabricated_scientific_image_count,
        "MathematicaProductPathClaimCount": safety["mathematica_product_path_count"],
        "BrokenInternalLinkCount": broken_internal_link_count,
        "BrokenImageCount": broken_image_count,
        "NewAiStyleEnDashCount": safety["en_dash_count"],
        "NewAiStyleEmDashCount": safety["em_dash_count"],
        "CnamePreservedQ": cname_exact,
        "NewCanonicalYeeScreenshotCount": published_count,
        "ChronologicalFrameSequenceQ": chronological,
        "PreviousFeaturedScreenshotSetRemovedQ": superseded_count == 0,
        "InteractiveCanonicalYeeCapabilityDescriptionUpdatedQ": WORKBENCH_SECTION_HEADING in parser.headings,
        "CapabilityFocusedPublicCopyQ": only_implemented_capabilities,
        "RepeatedNegativeDisclaimerCount": safety["repeated_negative_count"],
        "UnsupportedClaimCount": safety["unsupported_claim_count"],
        "PublicRoadmapLinkCount": safety["roadmap_link_count"],
        "PublicCopyPrivatePathOrIdentifierCount": private_copy_indicator_count,
        "BrokenImageReferenceCount": broken_image_count,
        "BrokenLocalLinkCount": broken_internal_link_count,
        "ExternalAssetDependencyAddedCount": homepage_external_assets + site_external_assets,
        "CnameUnchangedQ": cname_exact,
        "LegalPagesPreservedQ": legal_preserved,
        "AccessibilityValidationPassQ": accessibility_pass,
        "ResponsiveLayoutValidationPassQ": responsive_pass,
        "AncillaryPngMetadataChunkCount": metadata_chunk_count,
        "RawIncomingAssetStagedCount": len(raw_incoming),
    }
    summary["ValidationPassQ"] = not failures
    return failures, summary


def main() -> int:
    failures, summary = validate()
    for key, value in summary.items():
        if isinstance(value, bool):
            value = "True" if value else "False"
        print(f"{key}: {value}")
    if failures:
        print("\nVALIDATION FAILED", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
