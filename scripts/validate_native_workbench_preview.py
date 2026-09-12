#!/usr/bin/env python3
"""Offline company-site, screenshot-integrity and publication-safety checks.
Historical PNG, CRC, pixel, privacy and legal guards remain enforced.
No network, file writes, private imports or application execution.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import zlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = "assets/images/dad-fieldworks/native-workflow-2026-09"
PRESENTATION = ASSET_DIR + "/presentation.json"
NOTICE = "Development preview. External validation is not yet complete. Not released for production use."
OWNER = "DigitalArtDeco Labs UG (haftungsbeschränkt)"
PROTECTED = {
    ASSET_DIR + "/manifest.json": "3c9e43454a59e1e2e5758f16c067c5d3cb90ba1d2875c21f517fbbe54fbee5e5",
    "CNAME": "a0fcc58c50dbc063e7b42af68f9dce31ea6448863474fbb7848feae732245b4e",
    "COPYRIGHT.md": "17ef284402988e72a6150331b74e14928f0052f1c160aae9027f515b9f23b624",
    "LICENSE_NOTICE.md": "69a949a8032a3181a9ffaf168d0785610b3bd858549fc28a060033095863b739",
    "assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-02.png": "f7f69083156dff0c9fa094f28b744523630cd580263b0c9ae6a7bc5cb47b200b",
    "assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-03.png": "6bb7ab23ab9386aa42ff96a822d2cd27be25a586e0c1339cf10d1a125f76e729",
    "assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-04.png": "e836192e7a6fdf9a4c28d04f58a02a7b77805f0f7f0da69264eb5c04a280ab8e",
    "assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-05.png": "d4d1702c5c3078daf1336f59421e6de6bad9b0d09f0b5171488305132ae301f3",
    "assets/images/dad-fieldworks/canonical-yee/manifest.json": "d60de43e39de8eef9bd4a31c5584ae9f54490f288f167a37af843f0515015947",
    "docs/canonical_yee_field_visualization_provenance.md": "b4c14064bd1272bfb8d5b507400c39d892c848d2fa645a04b227e404edf4fee1",
    "docs/legal_site_identity_audit.md": "fbb8f102aace809fda29fcfb8a50162bc24750fdadecce746aa02c703983bf4d"
}
APPROVED = {
    "simulation-results": {
        "source": "01-main-current-viewer-actions.png",
        "source_sha256": "6b95656a17d6a91c1d3f27ed9a746012b9401dd52bad29d93b360db6cbb47685",
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "pixels": {
            "full": "02786c90ebfd62bf911ac06a19e739b0a48d5cc699c810149125762f3524312f"
        }
    },
    "compiled-geometry": {
        "source": "Screenshot (13).png",
        "source_sha256": "0d94acff436fbace43dd7869068a66fe7458949bd08226aa18edac1c8be82844",
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "pixels": {
            "full": "f8cddaa836377919f01d3626398af4e4e0182e3a1c73878394aa998213ccac40"
        }
    },
    "cartesian-s-parameters": {
        "source": "Screenshot (10).png",
        "source_sha256": "91ee16c20814ec6e49ed78c75dae4805253d3271d0fdfc5e31cc9e30392f3799",
        "crop": [
            30,
            24,
            1117,
            737
        ],
        "pixels": {
            "full": "f366fffeb9a4bc8aed577e2c9f4b225a1ee6b14467f882fd0b6beb1a59c8fea9"
        }
    },
    "smith-chart": {
        "source": "Screenshot (4).png",
        "source_sha256": "dcf5b40b9ae627ae0a95009d63e8b9e9d2d85e1b97bf66f99678ca695efcc2b6",
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "pixels": {
            "full": "407cffbf9f3e572ddfdc1be582b9eb149adc24c2daa421426924c57a3de5a876",
            "preview": "b0e0472165c0ac71872bec156e8997e49a8ecd1c5be7d9ce45855b3e8d6e6fc3"
        }
    },
    "native-hy-field": {
        "source": "Screenshot (7).png",
        "source_sha256": "516c67c4ca5585f1ea552510b4a31eabf7be3153e4e53677bd03944e2f49d1fb",
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "pixels": {
            "full": "61fba3fcfb055f082e392f6b9850d6508d0987e9dcde15e0d188e2edb8e0e251",
            "preview": "d0dcbc907d4b6eddbefa5ca006aacac267a5aca721ba9fc4972f7eb19c5ee23a"
        }
    },
    "native-ez-field": {
        "source": "Screenshot (6).png",
        "source_sha256": "e0b7a02ed164e84fa5edb220c367a2cb25f20287e8890447b5223f9eb92df116",
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "pixels": {
            "full": "c48078471d3560fe967965eb4e5a05162bd1b5d7d6090730e7170c745d47e2c4"
        }
    }
}
SOLVER_DIR = "assets/images/solver-development"
SOLVER_APPROVED = {
    "pulse-reference": {
        "sha256": "e74c69498a47209af4f3fd0bbc4104950605ba0e8616ceca65ce8a8d3cf4227e",
        "width": 1360,
        "height": 850,
        "bytes": 82343,
        "detail": "views/solver-pulse-reference.html"
    },
    "returning-wave-check": {
        "sha256": "b1a21141272ed1dd0acd9e3e88e0dbc714dd55d879aaf82dde835cbbb0195d1a",
        "width": 1360,
        "height": 850,
        "bytes": 147497,
        "detail": "views/solver-returning-wave.html"
    }
}
SOLVER_PAGES = ["solver-development.html"] + [value["detail"] for value in SOLVER_APPROVED.values()]
SOLVER_NOTICE = "These examples document selected internal numerical checks under defined test conditions. They do not represent external certification or a general accuracy guarantee."
CURRENT_DIR = "assets/images/dad-fieldworks/application-2026-09-09"
REFRESH_DIR = "assets/images/dad-fieldworks/application-2026-09-12"
REFRESH_APPROVED = {
    "hy-longitudinal": {
        "original": "codex-clipboard-60dbf1bd-80e9-4128-b651-95eca28fb816.png",
        "source_sha256": "ae655e5e2432fb24a81f8383a79d21efc432a1bb79e576c33800482527b44858",
        "source_size": [
            1440,
            900
        ],
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "preview_crop": [
            14,
            321,
            1426,
            802
        ],
        "sha256": "820b8dec9e7254a0cec3e55b9a6c9a9e72f0a8adc33208ee0e4601197e0cdcc9",
        "rgba_sha256": "56bad06c1388a11f1c8c49c646e13d9d63614e4e3abc4b98737ec9f99024bda6",
        "width": 1440,
        "height": 860,
        "preview": {
            "derivative": "hy-longitudinal-preview.png",
            "width": 1412,
            "height": 481,
            "sha256": "c771bd91e0bebfbbb5364f97f41a44be2b8507f58e884d7b7ea7acf81ff369bb",
            "rgba_sha256": "befbb33a1ea0c7bbbaac4f2a9e94397438b0d3466530efc40af5459af7d09cbd",
            "bytes": 65316
        }
    },
    "hy-transverse": {
        "original": "codex-clipboard-24720fbb-25e7-4f79-8967-5ef8366672c8.png",
        "source_sha256": "e2cdeb3531c9eef65bada96d7327e3cd4f3601f77655689b35aaf59bc8cd3192",
        "source_size": [
            1440,
            900
        ],
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "preview_crop": [
            14,
            321,
            1426,
            802
        ],
        "sha256": "ac674d409380ca301dac561b56761ff6d35b88d1dc40df551f54df90bcc94ecd",
        "rgba_sha256": "1ad363d0685388a4ffaa486d6a5754ff0aea0f57954e1b826225485c0bb4b84b",
        "width": 1440,
        "height": 860,
        "preview": {
            "derivative": "hy-transverse-preview.png",
            "width": 1412,
            "height": 481,
            "sha256": "f398fe1fc5afa8613c74cd2915f89e5e3e29aaee191e1a357a0ac365e560d7d4",
            "rgba_sha256": "735aed4879e5b7c5448677bc7205d59d3f89a4dbc036ccfe8c7f93cded61048b",
            "bytes": 42624
        }
    },
    "hy-contours": {
        "original": "codex-clipboard-9034cd52-5804-48cd-b32c-ecbc6cbcc238.png",
        "source_sha256": "0b348779c9c9fcaeecb5598a79300a1801758f53721968f83cf007658d573f9c",
        "source_size": [
            1440,
            900
        ],
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "preview_crop": [
            14,
            321,
            1426,
            802
        ],
        "sha256": "3d00b042970a7883f976977efa78feffd30c44ca86d35fef492d8f796a896157",
        "rgba_sha256": "99f8d456a40c03dc235ceb3389011be3d1e9d82e9f895cf424c4e978834652dc",
        "width": 1440,
        "height": 860,
        "preview": {
            "derivative": "hy-contours-preview.png",
            "width": 1412,
            "height": 481,
            "sha256": "62c9c8e7b5ebf1690c93fc306c2da0c8dc21e0d0bdaf99411ab1f5ee4fa4e747",
            "rgba_sha256": "e1fa8d1c436b580d835c2e12f1a527d5c98234014d2af7f57c31940a5b5be521",
            "bytes": 48341
        }
    },
    "reference-model": {
        "original": "codex-clipboard-585f9d09-ee3b-4b96-8f49-ce0d874b1268.png",
        "source_sha256": "6d4d724b32c796d26646f2785ed1c9d3e2874227ab4d3e9d87ade3c41f17d114",
        "source_size": [
            1440,
            900
        ],
        "crop": [
            307,
            86,
            1439,
            836
        ],
        "sha256": "ece45a1759feb6dcf68042b037ceeb8f425778e3444fad99de64a2f4c02b70d2",
        "rgba_sha256": "d4f5774f0f6612b2c44741834e79291c2a5c06d56aac268b12982aa89900cad0",
        "width": 1132,
        "height": 750
    },
    "smith-chart": {
        "original": "Screenshot (63).png",
        "source_sha256": "dabc7a1e5c02a69adda5c98dcaf9f7330a0667baa7b76a91f103a9ff75826340",
        "source_size": [
            1440,
            900
        ],
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "sha256": "8112f7b5c327978aa6e16b36660b356249ac4bf235cf074c6735259f9f28140c",
        "rgba_sha256": "4aca21f63c370b9abb01629eeaf6001f054e9b8656fe8345ec6c3e31232a0a72",
        "width": 1440,
        "height": 860
    }
}
REFRESH_PAGES = ["views/" + key + ".html" for key in REFRESH_APPROVED]
PRODUCT_NOTICE = "DAD FieldWorks is in development. The images show the current application."
BRAND_IMAGES = {
    "assets/brand/dad_fieldworks_blue_field_sculpture.png": "7b96ba79717d49f29df838e390e249c171511b4f0d912272c7cba50ddce2001d",
    "assets/brand/dad_fieldworks_blue_field_sculpture-256.png": "4a7ed4ec5892eb3bbc0b6e3c4e0ef78e19e99f89702edd80d40c353729c7224d"
}
CURRENT_NOTES = ["current_public_status", "claim_boundaries", "company_screenshot_provenance", "publication_notes"]
ACTIVE = ["index.html", "README.md", "docs/current_public_status.md", "docs/claim_boundaries.md",
          "docs/company_screenshot_provenance.md", "assets/hero/README.md"]
NEW_DOCS = ["docs/README.md", "assets/asset_manifest.md"]
LEGACY_VIEWS = ["simulation-results", "compiled-geometry", "native-hy-field", "native-ez-field"]
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".md", ".txt", ".xml", ".yml", ".yaml"}
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
MATHEMATICA_PRODUCT_PATTERN = re.compile(r"(?i)\b(?:mathematica|wolfram)\b")
SCIENTIFIC_IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}

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



# New preview notices are required, not treated as forbidden negative wording.
UNSUPPORTED_CLAIM_PATTERNS += (
    re.compile(r"\b(?:revolutionary|game-changing|unparalleled)\b", re.I),
    re.compile(r"\b(?:buy now|download the software|bundled results included)\b", re.I),
    re.compile(r"\breleased for production use\b", re.I),
)
TOKEN_PATTERN = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
FORBIDDEN_SUFFIXES = {".exe", ".dll", ".pdb", ".cpp", ".hpp", ".h", ".c", ".obj", ".lib", ".zip", ".7z"}
FAILURES = []

def check(condition, message):
    if not condition:
        FAILURES.append(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8", check=True,
                            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    return result.stdout

def public_files():
    return sorted(set(git("ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0")) - {""})

def unsupported(text):
    findings = []
    for pattern in UNSUPPORTED_CLAIM_PATTERNS:
        for match in pattern.finditer(text):
            prefix = text[max(0, match.start()-55):match.start()]
            if not re.search(r"\b(?:not|no|never|without)\s+(?:[\w-]+\s+){0,3}$", prefix, re.I):
                findings.append(match.group())
    return findings

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.hrefs, self.resources, self.images = set(), [], [], []
        self.tags, self.data, self.scripts, self.metas = [], [], [], {}
        self.figures, self._figure_stack = [], []
        self.feed(text)
        self.close()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if tag == "figure":
            check(not self._figure_stack, "Nested figure elements")
            self._figure_stack.append({"images": [], "data": []})
        if "id" in a:
            check(a["id"] not in self.ids, "Duplicate HTML ID: " + a["id"])
            self.ids.add(a["id"])
        for key in a:
            check(not key.startswith("on"), "Executable inline event attribute: " + key)
        if tag == "a":
            self.hrefs.append(a.get("href", ""))
        if tag == "img":
            self.images.append(a)
            if self._figure_stack:
                self._figure_stack[-1]["images"].append(a)
            self.resources.append(a.get("src", ""))
            for entry in a.get("srcset", "").split(","):
                if entry.strip():
                    self.resources.append(entry.strip().split()[0])
        if tag in {"iframe", "embed", "object", "form", "video", "audio"}:
            check(False, "Unexpected active/embed/form element: " + tag)
        if tag == "script":
            self.scripts.append(a)
            check(a.get("type") == "application/ld+json" and "src" not in a,
                  "Executable page JavaScript is not authorized")
        if tag == "link" and a.get("rel") in {"stylesheet", "icon", "preload"}:
            self.resources.append(a.get("href", ""))
        if tag == "meta":
            self.metas[a.get("name", a.get("property", ""))] = a.get("content", "")
    def handle_data(self, data):
        self.data.append(data)
        if self._figure_stack:
            self._figure_stack[-1]["data"].append(data)
    def handle_endtag(self, tag):
        if tag == "figure" and self._figure_stack:
            self.figures.append(self._figure_stack.pop())
    @property
    def text(self):
        return re.sub(r"\s+", " ", " ".join(self.data)).strip()

def local_target(source, target):
    u = urlsplit(target)
    if u.scheme or target.startswith("//"):
        return None, u.fragment
    p = source if not u.path else ((ROOT / unquote(u.path).lstrip("/")) if u.path.startswith("/") else (source.parent / unquote(u.path)))
    p = p.resolve()
    check(p.is_relative_to(ROOT), "Local link escapes website: " + target)
    return p, u.fragment

def markdown_ids(text):
    return {re.sub(r"[^\w -]", "", line.lower()).replace(" ", "-")
            for line in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", text)}

def link_check(source, target, resource=False):
    check(bool(target), "Empty link/resource in " + source.name)
    check(not PRIVATE_PATH_PATTERN.search(target), "Private link in " + source.name)
    u = urlsplit(target)
    check(u.scheme.lower() not in {"javascript", "data", "file"}, "Unsafe link scheme")
    if resource:
        check(not u.scheme and not target.startswith("//"), "External runtime asset: " + target)
    p, fragment = local_target(source, target)
    if p is None:
        return
    check(p.is_file(), "Missing local target: " + str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else "Escaping target")
    if p.is_file() and fragment:
        if p.suffix == ".html":
            check(fragment in Page(p.read_text(encoding="utf-8")).ids, "Missing HTML anchor: " + target)
        elif p.suffix == ".md":
            check(fragment in markdown_ids(p.read_text(encoding="utf-8")), "Missing Markdown anchor: " + target)

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

    rgba = pixels if bytes_per_pixel == 4 else bytearray(channel for pos in range(0, len(pixels), 3) for channel in (*pixels[pos:pos+3], 255))
    return {
        "rgba_pixel_sha256": hashlib.sha256(rgba).hexdigest(),
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "chunks": chunks,
        "pixel_sha256": hashlib.sha256(pixels).hexdigest(),
    }



CURRENT_APPROVED = {
    "pcb-geometry": {
        "id": "pcb-geometry",
        "original": "Screenshot (43).png",
        "source_sha256": "db0f6b05ed09e9a31ee1e099164cbbebe55b4705482bfcf9c24bee42622d51e0",
        "source_size": [
            1440,
            857
        ],
        "crop": [
            347,
            103,
            1438,
            835
        ],
        "width": 1091,
        "height": 732,
        "sha256": "eeb442d017e5b6095fcf71391380915cb2ebfebcd3ec98384664195548c25461",
        "rgba_sha256": "f272d2549b72cf74b6ef79ca8d45b81f80cfccf0fe426ac04bcaecc952eb049d"
    },
    "rf-sketcher": {
        "id": "rf-sketcher",
        "original": "Screenshot (42).png",
        "source_sha256": "35d42cfadecbac3d2f66c3730ac9ba4283999e787fba2ea8f1744ff3eb1e4c85",
        "source_size": [
            1440,
            859
        ],
        "crop": [
            0,
            0,
            1440,
            859
        ],
        "width": 1440,
        "height": 859,
        "sha256": "9c66d61f632c019b0ce0ff96d0fe63b248e18cbbe3febbad5a4aa20ec48a5e72",
        "rgba_sha256": "f45f466b003f2a5f606047a7d6e0a6dc7899899c761a19a55bc84a01828e3107"
    },
    "cartesian-s-parameters": {
        "id": "cartesian-s-parameters",
        "original": "Screenshot (37).png",
        "source_sha256": "2ec17eb66b08f038b5e97c472c99ee200116e3c5201a7748f03285ad5190f28a",
        "source_size": [
            1440,
            859
        ],
        "crop": [
            0,
            0,
            1440,
            859
        ],
        "width": 1440,
        "height": 859,
        "sha256": "774611335baf1274b37fca57ba96d30a5d601510cd37ef7a73b27cad4921ebde",
        "rgba_sha256": "eeab3ffc5714f8451c1a8ef703e168ec48bfe142cd3becca09f2eedf5a4511c5"
    },
    "smith-chart": {
        "id": "smith-chart",
        "original": "Screenshot (38).png",
        "source_sha256": "3f23148ab4dc0888e1882807dee7b19247bbb2a4950e7eb6eb46565e384490f9",
        "source_size": [
            1440,
            860
        ],
        "crop": [
            0,
            0,
            1440,
            860
        ],
        "width": 1440,
        "height": 860,
        "sha256": "f9ab24ba81f98cb278dbf903d5957680ecc873df4d0c4af5163b2310e8593469",
        "rgba_sha256": "c9890d38bff5c89b077dea06c5195c31e5e2588c46d26df62d1d56cbf8be2a27"
    },
    "magnetic-field": {
        "id": "magnetic-field",
        "original": "Screenshot (41).png",
        "source_sha256": "86c70545710cb95664bce50a4e532d23321cfb8e6ac286b22b735a6133d434b9",
        "source_size": [
            1440,
            859
        ],
        "crop": [
            0,
            0,
            1440,
            859
        ],
        "width": 1440,
        "height": 859,
        "sha256": "edf54bf1f39bc9f0cf672c4fbc8d13064afb0db2040178e2502c20a2a4caf264",
        "rgba_sha256": "fa88662a56ee5e0349c96ce33df389554c0f0892cd7a685d7f63bf59bd878b90"
    }
}

PROTECTED.update({
    "assets/images/dad-fieldworks/native-workflow-2026-09/presentation.json": "71e5380c66c01e864c98bbdb7810dba021523cb37340a594baa158ec4513f9b6",
    "docs/native_workflow_screenshot_provenance.md": "32e113c4c505f7bd968aa5fcdea9cde6f4390aeec85d6e39732dad9279347898",
    "docs/showcase_refresh_2026_09.md": "1f7e4db55785fe07d95f24efab1eb96ff2ca00a6befb063921e3a9e1d8714e28",
    "docs/product_communication_review_2026_09.md": "b2f0c87ef09834adb7e36633401f28ae2f6eb207b200b1f0c24973be481cb706"
})

def legal_core(raw, name):
    text = re.search(r'<div class="legal-panel">([\s\S]*?)</div>', raw).group(1)
    if name == "impressum.html":
        text = re.sub(r'<h3>Hinweis zur Website</h3>\s*<p>[\s\S]*?</p>', '', text)
    else:
        text = re.sub(r'(<h2>Allgemeine Hinweise</h2>\s*<p>)[\s\S]*?(Personenbezogene Daten)', r'\1\2', text, count=1)
    return hashlib.sha256(text.replace('\r\n','\n').encode('utf-8')).hexdigest()

LEGAL_CORE_HASHES = {
    "impressum.html": "a20f448912742fa2082300fb307305aabf9cd719b1670359c5b10966857d8fda",
    "datenschutz.html": "7593ade5791f52504c9b5d7a27657aec024a10866e4f69e3297fede01bf83f60"
}

def legal_footer_audit(raw, rel):
    """Both legal languages must be directly linked in every page footer."""
    match = re.search(r'<footer(?:\s[^>]*)?>([\s\S]*?)</footer>', raw)
    check(match is not None, "Footer missing: " + rel)
    if match is None:
        return
    footer = Page(match.group(1))
    targets = {local_target(ROOT / rel, href)[0] for href in footer.hrefs}
    for name in ["impressum.html", "legal-notice.html", "datenschutz.html"]:
        check((ROOT / name).resolve() in targets, "Footer legal link missing: " + rel + " -> " + name)
    for label in ["Impressum (DE)", "Legal Notice (EN)"]:
        check(label in footer.text, "Footer legal language label missing: " + rel + " -> " + label)


def legal_translation_audit(german_raw, english_raw):
    """Retain verified identity, translated sections and reciprocal language links."""
    english = Page(english_raw)
    for value in [OWNER, "Sperberweg 27", "86609 Donauwörth", "Germany",
                  "Managing Director Harun Aktas", "Amtsgericht Augsburg", "HRB 43034",
                  "VAT ID: DE464701318", "info@dadlabs.de", "+49 176 48296275",
                  "Information pursuant to Section 5 DDG",
                  "English translation of the German Impressum."]:
        check(value in english.text, "English legal fact missing: " + value)
    check("1260195" not in english.text, "Disallowed English register identifier")
    check({"mailto:info@dadlabs.de", "tel:+4917648296275"} <= set(english.hrefs),
          "English legal contact links changed")
    headings = [Page(value).text for value in re.findall(r'<h3>(.*?)</h3>', english_raw, re.S)]
    check(headings == ["Service provider and website operator", "Represented by",
                      "Commercial register", "VAT identification number", "Contact",
                      "About this website", "Liability for content", "Liability for links", "Copyright"],
          "English legal section coverage changed")
    check(re.search(r'<h1[^>]*>Legal Notice</h1>', english_raw), "English legal title changed")
    languages = {"de": "impressum.html", "en": "legal-notice.html"}
    for language, raw in [("de", german_raw), ("en", english_raw)]:
        rel = languages[language]
        page = Page(raw)
        canonical = [a.get("href") for tag, a in page.tags if tag == "link" and a.get("rel") == "canonical"]
        check(canonical == ["https://www.dadlabs.de/" + rel], "Legal canonical URL changed: " + rel)
        alternates = {a.get("hreflang"): a.get("href") for tag, a in page.tags
                      if tag == "link" and a.get("rel") == "alternate"}
        check(alternates == {lang: "https://www.dadlabs.de/" + name for lang, name in languages.items()},
              "Legal language metadata missing: " + rel)
        switch = re.search(r'<nav class="legal-languages"[^>]*>([\s\S]*?)</nav>', raw)
        check(switch is not None, "Legal language switch missing: " + rel)
        if switch is None:
            continue
        anchors = [a for tag, a in Page(switch.group(1)).tags if tag == "a"]
        check(len(anchors) == 2, "Expected two legal language links: " + rel)
        for lang, name in languages.items():
            matches = [a for a in anchors if a.get("href") == name and a.get("lang") == lang
                       and a.get("hreflang") == lang]
            check(len(matches) == 1, "Legal language link missing: " + rel + " -> " + name)
            if len(matches) == 1:
                check((matches[0].get("aria-current") == "page") == (language == lang),
                      "Legal active language incorrect: " + rel)


def validate_historical():
    manifest = json.loads((ROOT / ASSET_DIR / "manifest.json").read_text(encoding="utf-8"))
    check(manifest["owner"] == OWNER, "Screenshot copyright owner changed")
    check(manifest["source_date"] == "2026-09-05", "Capture date changed")
    check(manifest["scientific_content_changed"] is False and manifest["generated_scientific_images"] == 0,
          "Scientific asset processing authority changed")
    check("Not supplied" in manifest["executable_provenance"], "Missing executable provenance boundary")
    check([i["id"] for i in manifest["images"]] == list(APPROVED), "Approved six-view selection/order changed")
    presentation = json.loads((ROOT / PRESENTATION).read_text(encoding="utf-8"))
    check(presentation.get("source_manifest") == "manifest.json", "Presentation source changed")
    check([i["id"] for i in presentation["images"]] == list(APPROVED), "Presentation selection differs")
    current_copy = {i["id"]: i for i in presentation["images"]}
    for item in current_copy.values():
        check(set(item) == {"id", "title", "caption", "alt", "detail"},
              "Editorial copy cannot override provenance or derivatives")
        check(all(isinstance(item.get(k), str) and item[k].strip()
                  for k in ("title", "caption", "alt", "detail")), "Missing editorial screenshot copy")
    allowed_images, full_images = set(), {}
    total_bytes = 0
    for item in manifest["images"]:
        approved = APPROVED[item["id"]]
        check(item["source_filename"] == approved["source"] and item["source_sha256"] == approved["source_sha256"],
              "Unapproved source identity: " + item["id"])
        check((item["source_width"], item["source_height"]) == (1440, 900), "Original dimensions changed")
        c = item["crop"]
        check([c["left"], c["top"], c["right"], c["bottom"]] == approved["crop"], "Unapproved crop: " + item["id"])
        check(c["coordinates"] == "right and bottom exclusive", "Crop convention changed")
        check(all(item.get(k) for k in ("role", "caption", "alt", "title")), "Missing caption/role/alt")
        check([v["kind"] for v in item["derivatives"]] == list(approved["pixels"]), "Unexpected derivative selection")
        for v in item["derivatives"]:
            rel = v["path"]
            expected_name = item["id"] + ("-720" if v["kind"] == "preview" else "") + ".png"
            check(rel == ASSET_DIR + "/" + expected_name, "Derivative path not authorized")
            allowed_images.add(rel)
            p = ROOT / rel
            check(p.is_file() and not p.is_symlink(), "Missing or linked image " + rel)
            if not p.is_file():
                continue
            png = read_png(p)
            check(sha(p) == v["sha256"] and p.stat().st_size == v["bytes"], "File identity mismatch: " + rel)
            check(png["rgba_pixel_sha256"] == v["rgba_pixel_sha256"] == approved["pixels"][v["kind"]],
                  "Approved pixel identity mismatch: " + rel)
            check(set(png["chunks"]) == {"IHDR", "IDAT", "IEND"}, "PNG metadata or unexpected chunk: " + rel)
            width = c["right"] - c["left"]
            height = c["bottom"] - c["top"]
            expected = (width, height) if v["kind"] == "full" else (720, round(height*720/width))
            check((png["width"], png["height"]) == (v["width"], v["height"]) == expected, "Image dimensions: " + rel)
            if v["kind"] == "preview":
                check(v["bytes"] < item["derivatives"][0]["bytes"], "Preview larger than full PNG")
            else:
                full_images[item["id"]] = v
            total_bytes += v["bytes"]
    actual_images = {p.relative_to(ROOT).as_posix() for p in (ROOT / ASSET_DIR).glob("*.png")}
    check(actual_images == allowed_images, "Unmanifested or missing current PNG")
    check(len(allowed_images) == 8, "Expected six full crops and two smaller previews")

    return {"captures": len(APPROVED), "pngs": len(allowed_images), "bytes": total_bytes}


def section(raw, name):
    match = re.search(r'<section[^>]*id="' + re.escape(name) + r'"[\s\S]*?</section>', raw)
    check(bool(match), "Missing section: " + name)
    return Page(match.group()).text if match else ""

def document_source_audit(source, rendered, stem):
    """Preserve paragraphs, list items and table cells, including limitations."""
    for line in source.splitlines():
        line=line.strip()
        if not line or re.fullmatch(r"[| :\-]+",line):
            continue
        line=re.sub(r"^(?:#{1,6}\s+|[-*+]\s+|\d+\.\s+)", "", line)
        line=re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",line).replace(chr(96),"")
        pieces=line.strip("|").split("|") if line.startswith("|") else [line]
        for piece in pieces:
            text=re.sub(r"\s+","",piece)
            check(not text or text in re.sub(r"\s+","",rendered), "Source content lost: "+stem+"/"+piece[:50])

def copy_quality_audit(raw):
    clean = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", raw, flags=re.I)
    body = re.search(r"<body\b[^>]*>([\s\S]*?)</body>", clean, re.I).group(1)
    visible_body = re.sub(r'<span class="sr-only">[\s\S]*?</span>', "", body)
    page, visible = Page(clean), Page(visible_body).text
    labels = " ".join(a.get(k, "") for _, a in page.tags for k in ("alt", "aria-label"))
    semantic = visible + " " + " ".join(page.metas.values()) + " " + labels
    forbidden = ("DAD-owned", "component-native", "explicit contracts", "evidence-bound",
                 "current-state authority", "source authority", "North Star",
                 "DecisionClass", "FailureClass", "fail-closed")
    counts = {term: len(re.findall(r"\b"+re.escape(term)+r"\b", semantic, re.I))
              for term in forbidden + ("native", "evidence-controlled")}
    check(all(counts[t] == 0 for t in forbidden), "Internal terminology in homepage")
    check(counts["native"] <= 2 and counts["evidence-controlled"] <= 1, "Homepage terminology budget")
    check(not re.search(r"\b(?:powerful|seamless|cutting-edge|revolutionary|next-generation|game-changing|unmatched|unparalleled|professional|HFSS|CST|Sonnet|COMSOL)\b", semantic, re.I), "Hype/comparison in homepage")
    check(not re.search(r"[\u2013\u2014]", semantic), "En/em dash in homepage")
    check(not re.search(r"\b(?:faster|cheaper|more accurate|market leader|save[s]?\s+\d+|reduce[s]?\s+.{0,15}(?:time|cost))\b", semantic, re.I), "Unsupported benefit")
    hero = section(raw, "company")
    product, outlook = section(raw, "fieldworks"), section(raw, "outlook")
    check("DigitalArtDeco Labs" in hero and "We develop software for electromagnetic simulation." in hero, "Company must lead the hero")
    check("RF, microwave, signal integrity and PCB engineers" in hero, "Audience missing")
    check("Windows desktop workspace" in product and PRODUCT_NOTICE in product, "Product/status missing")
    check(visible.count(PRODUCT_NOTICE) == 1, "Expected one calm product status")
    check("Tuto example shows construction" in product and "different project" in product, "Examples conflated")
    check("saved time-domain views, not fields at the frequency" in product and "linear magnitude, not dB" in product, "Scientific interpretation note missing")
    check("not a time sequence" in product and "not solver cell occupancy" in product and "signed H_y in A/m" in product,
          "Field view context missing")
    check("We plan to extend" in outlook and "development goals, not a list of capabilities available today" in outlook, "Future direction not separated")
    current_sections = hero + section(raw,"focus") + product + section(raw,"contact")
    check(not re.search(r"\b(?:printed antennas|loss models|far[- ]fields?|antenna gain|optimization|coaxial)\b", current_sections, re.I), "Future capability promoted")
    check("mailto:info@dadlabs.de" in page.hrefs and "tel:+4917648296275" in page.hrefs, "Contact route changed")
    check(not any("evidence_contract" in x for x in page.hrefs), "Architecture promoted in homepage")
    return {"term_counts": counts, "visible_words": len(visible.split()), "company_first": True,
            "current_future_separated": True, "single_product_status": True}

def validate_solver_development():
    manifest_path = SOLVER_DIR + "/manifest.json"
    record = json.loads((ROOT / manifest_path).read_text(encoding="utf-8"))
    check(record.get("owner") == OWNER, "Solver diagnostic copyright changed")
    check(record.get("processing") == "Original PNG bytes, dimensions and scientific content preserved. No cropping, resampling, smoothing or generated curves.",
          "Solver diagnostic original-byte boundary missing")
    check("not independent experimental studies" in record.get("context", ""), "Related solver figures misrepresented")
    check([item.get("id") for item in record["images"]] == list(SOLVER_APPROVED), "Solver figure selection changed")
    raw = (ROOT / "solver-development.html").read_text(encoding="utf-8")
    main = Page(raw)
    main_content = Page(re.search(r'<main[^>]*>([\s\S]*?)</main>', raw).group(1)).text
    words = len(main_content.split())
    check(300 <= words <= 450, "Solver page should be 300 to 450 words: " + str(words))
    check(SOLVER_NOTICE in main.text, "Solver verification boundary missing")
    for phrase in ["FDTD", "finite difference time domain", "not a measurement",
                   "same uniform TEM pulse-source study", "not two independent studies"]:
        check(phrase in main.text, "Solver scientific context missing: " + phrase)
    images = set()
    for item in record["images"]:
        approved = SOLVER_APPROVED[item["id"]]
        rel = SOLVER_DIR + "/" + item["id"] + ".png"
        images.add(rel)
        check(item.get("path") == rel, "Unapproved solver asset path")
        check(set(item) == {"id", "path", "sha256", "width", "height", "bytes", "case", "title",
                            "purpose", "caption", "scope", "alt", "detail"}, "Private/unexpected solver manifest field")
        check(item.get("case") == "Uniform TEM pulse-source checks", "Solver case attribution changed")
        for key, value in approved.items():
            check(item.get(key) == value, "Solver diagnostic identity changed: " + key)
        png = read_png(ROOT / rel)
        check(sha(ROOT / rel) == approved["sha256"] and (ROOT / rel).stat().st_size == approved["bytes"],
              "Original solver PNG bytes changed: " + rel)
        check((png["width"], png["height"]) == (approved["width"], approved["height"]), "Solver PNG dimensions")
        check(all(item.get(key) for key in ["title", "purpose", "caption", "scope", "alt"]), "Solver caption/scope missing")
        detail = Page((ROOT / item["detail"]).read_text(encoding="utf-8"))
        check("../solver-development.html#" + item["id"] in detail.hrefs and "../" + rel in detail.hrefs,
              "Solver image navigation missing")
        check(SOLVER_NOTICE in detail.text, "Solver detail qualification boundary missing")
        for page, prefix in [(main, ""), (detail, "../")]:
            figures = [f for f in page.figures if any(a.get("src") == prefix + rel for a in f["images"])]
            check(len(figures) == 1, "Solver image missing or duplicated")
            if figures:
                a = figures[0]["images"][0]
                check(a.get("width") == str(approved["width"]) and a.get("height") == str(approved["height"]),
                      "Solver HTML image proportions changed")
                check(a.get("alt") == item["alt"] and item["caption"] in " ".join(figures[0]["data"]),
                      "Solver figure caption/alt differs from public provenance")
                if prefix == "":
                    check(a.get("loading") == "lazy", "Below-fold solver plot should lazy-load")
    check({p.relative_to(ROOT).as_posix() for p in (ROOT / SOLVER_DIR).iterdir()} == images | {manifest_path},
          "Unexpected file in solver asset publication directory")
    for rel in SOLVER_PAGES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        page = Page(text)
        title = re.search(r'<title>(.*?)</title>', text).group(1)
        check(page.metas.get("og:title") == page.metas.get("twitter:title") == title, "Solver social title")
        check(page.metas.get("og:description") == page.metas.get("twitter:description") == page.metas["description"],
              "Solver social description")
        check([a.get("href") for t, a in page.tags if t == "link" and a.get("rel") == "canonical"] ==
              ["https://www.dadlabs.de/" + rel], "Solver canonical URL")
        check(page.metas.get("og:url") == "https://www.dadlabs.de/" + rel, "Solver social URL")
        expected_image = record["images"][0] if rel == SOLVER_PAGES[0] else next(i for i in record["images"] if i["detail"] == rel)
        check(page.metas.get("og:image") == page.metas.get("twitter:image") == "https://www.dadlabs.de/" + expected_image["path"],
              "Solver social image")
        check(page.metas.get("og:image:alt") == page.metas.get("twitter:image:alt") == expected_image["alt"], "Solver social alt")
        check(page.metas.get("og:image:width") == str(expected_image["width"]) and
              page.metas.get("og:image:height") == str(expected_image["height"]), "Solver social dimensions")
        check(not re.search(r"\b(?:FTDT|Feko|fully validated|externally verified|industry leading|unmatched accuracy|DAD-owned|component-native|explicit contracts)\b", page.text, re.I),
              "Inappropriate solver public claim")
    return images, {"figures": len(images), "main_words": words, "original_png_bytes": sum(i["bytes"] for i in record["images"])}


def validate_refresh():
    """Pin originals, crop pixels, interpretation and the active Smith replacement."""
    manifest = json.loads((ROOT / REFRESH_DIR / "manifest.json").read_text(encoding="utf-8"))
    recipe = json.loads((ROOT / REFRESH_DIR / "source-selection.json").read_text(encoding="utf-8"))
    check(manifest["date"] == recipe["date"] == "2026-09-13", "New screenshot selection date")
    check(manifest["context"] == recipe["context"] and "not a time sequence" in manifest["context"]
          and "not a field at a plot marker frequency" in manifest["context"], "Field timing context")
    check("no resampling" in manifest["processing"], "Unchanged pixel boundary")
    check([e["id"] for e in manifest["captures"]] == list(REFRESH_APPROVED), "New screenshot order")
    check([e["id"] for e in recipe["sources"]] == list(REFRESH_APPROVED), "New recipe order")
    home = Page((ROOT / "index.html").read_text(encoding="utf-8"))
    images, copy = set(), {}
    for entry, source in zip(manifest["captures"], recipe["sources"]):
        key = entry["id"]
        for name, value in REFRESH_APPROVED[key].items():
            check(entry.get(name) == value, "New image identity changed: " + key + "/" + name)
        check(all(entry.get(name) == value for name, value in source.items()), "New recipe/manifest mismatch")
        check(entry.get("origin") == "user-supplied application screenshot", "Image origin")
        check(entry.get("source_screen_date") == "2026-09-12" and entry.get("capture_date") is None,
              "Screen date must not become an asserted capture date")
        check(entry.get("group") == "Uniform Shielded TEM Reference Line", "Reference project changed")
        check(entry.get("detail") == "views/" + key + ".html", "New detail route")
        check(entry.get("derivative") == key + ".png", "New derivative name")
        check(all(entry.get(k) for k in ["title", "caption", "alt", "use", "view_kind"]), "Missing screenshot copy")
        for variant in [entry] + ([entry["preview"]] if "preview" in entry else []):
            rel = REFRESH_DIR + "/" + variant["derivative"]
            images.add(rel)
            png = read_png(ROOT / rel)
            check(sha(ROOT / rel) == variant["sha256"] and (ROOT / rel).stat().st_size == variant["bytes"],
                  "New PNG byte identity: " + rel)
            check(png["rgba_pixel_sha256"] == variant["rgba_sha256"], "New PNG pixels: " + rel)
            check((png["width"], png["height"]) == (variant["width"], variant["height"]), "New PNG dimensions")
            check(set(png["chunks"]) == {"IHDR", "IDAT", "IEND"}, "New PNG metadata")
        raw = (ROOT / entry["detail"]).read_text(encoding="utf-8")
        detail = Page(raw)
        full = REFRESH_DIR + "/" + entry["derivative"]
        check("../" + full in detail.hrefs and entry["detail"] in home.hrefs, "New image navigation")
        check("../index.html#fieldworks" in detail.hrefs or "../index.html#geometry-fields" in detail.hrefs,
              "New image gallery return")
        check(NOTICE in detail.text and "User-supplied application screenshot" in detail.text, "New detail status/origin")
        if key.startswith("hy-"):
            check(entry["component"] == "H_y" and entry["unit"] == "A/m" and entry["saved_step"] == 4096
                  and entry["saved_time_s"] == "1.023875e-09", "Saved component identity")
            axis, index = ("Y", 10) if key == "hy-longitudinal" else ("X", 21)
            mode = "Field with section contours" if key == "hy-contours" else "Field with transparent 3D geometry"
            check((entry["slice_normal"], entry["slice_index"], entry["display_mode"]) == (axis, index, mode), "Slice/mode identity")
            check(all(s in detail.text for s in ["H_y in A/m", "step 4096", "1.023875e-09 s",
                  "not a time sequence", "not compiled solver cells"]), "Field meaning boundary")
        elif key == "smith-chart":
            check((entry["s_parameter"], entry["frequency_marker_ghz"], entry["reference_impedance_ohm"],
                   entry["display_mode"]) == ("S(2,2)", "5.500", 50, "Smith: wavelength scales"), "Smith identity")
            check(entry["replaces"] == CURRENT_DIR + "/smith-chart.png", "Historical Smith replacement reference")
            check(all(s in detail.text for s in ["S(2,2)", "5.500 GHz", "50 ohm reference", "Gamma",
                  "wavelength scales", "not a measurement", "graphical aids", "deembedding result"]), "Smith meaning")
            check("Via Transition" not in raw and "2.800" not in raw and CURRENT_DIR not in raw, "Stale Smith copy/image")
        else:
            check("authoring geometry" in detail.text and "private project path" in detail.text
                  and "not a solver cell or mesh image" in detail.text, "Model crop/context")
        for page, prefix, variant in [(home, "", entry.get("preview", entry)), (detail, "../", entry)]:
            src = prefix + REFRESH_DIR + "/" + variant["derivative"]
            figures = [f for f in page.figures if any(i.get("src") == src for i in f["images"])]
            check(len(figures) == 1, "New figure missing/duplicated: " + src)
            if figures:
                image = figures[0]["images"][0]
                check(image.get("alt") == entry["alt"] and image.get("width") == str(variant["width"])
                      and image.get("height") == str(variant["height"]), "New figure alt/proportions")
                check(entry["caption"] in " ".join(figures[0]["data"]), "New figure caption/provenance")
        check(detail.metas.get("og:image") == detail.metas.get("twitter:image") == "https://www.dadlabs.de/" + full, "New social image")
        check(detail.metas.get("og:image:alt") == detail.metas.get("twitter:image:alt") == entry["alt"], "New social alt")
        check(detail.metas.get("og:image:width") == str(entry["width"]) and
              detail.metas.get("og:image:height") == str(entry["height"]), "New social image dimensions")
        title = re.search(r"<title>(.*?)</title>", raw).group(1)
        check(detail.metas.get("og:title") == detail.metas.get("twitter:title") == title, "New social title")
        check(detail.metas.get("og:description") == detail.metas.get("twitter:description") == detail.metas["description"], "New social description")
        check([a.get("href") for t, a in detail.tags if t == "link" and a.get("rel") == "canonical"] ==
              ["https://www.dadlabs.de/" + entry["detail"]], "New canonical")
        check(detail.metas.get("og:url") == "https://www.dadlabs.de/" + entry["detail"], "New social URL")
        copy[key] = entry
    check({p.relative_to(ROOT).as_posix() for p in (ROOT / REFRESH_DIR).iterdir()} ==
          images | {REFRESH_DIR + "/manifest.json", REFRESH_DIR + "/source-selection.json"}, "Unexpected new publication asset")
    return images, copy


def validate():
    paths = public_files()
    historical = validate_historical()
    solver_images, solver_report = validate_solver_development()
    refresh_images, refresh_copy = validate_refresh()
    brand_record = json.loads((ROOT/"assets/brand/blue_field_sculpture_manifest.json").read_text(encoding="utf-8"))
    check("Not scientific data" in brand_record["role"] and "Built-in image generation" in brand_record["method"], "Brand illustration classification missing")
    for rel, expected in BRAND_IMAGES.items():
        check(sha(ROOT/rel)==expected==brand_record["files"][Path(rel).name]["sha256"], "Approved brand artwork changed: "+rel)
    brand_png = read_png(ROOT/"assets/brand/dad_fieldworks_blue_field_sculpture-256.png")
    check((brand_png["width"],brand_png["height"])==(256,256), "Brand web derivative dimensions")
    for rel, expected in PROTECTED.items():
        check((ROOT/rel).is_file() and sha(ROOT/rel)==expected, "Protected historical/domain/license bytes changed: "+rel)
    check((ROOT/"CNAME").read_text().strip()=="www.dadlabs.de", "Domain changed")
    check(sha(ROOT/"favicon.ico")==brand_record["browser_icon"]["sha256"]=="3e54457e7d6308c5688bf87d613952a461216d73be08264f1aa782e9defa6b6a", "Approved new browser icon changed")
    check(sha(ROOT/"assets/brand/legacy_kernel_wave_favicon.ico")=="ae41a3988a5e832f30c484765370d6f66da9ae391d7a88b955995fb0b80f71ba", "Historical browser icon changed")
    check(sha(ROOT/"assets/brand/dad_fieldworks_kernel_wave_mark.png")=="410e6874da3d6f37bf02836c2ae107be27489f7db93421fb6a29b91af1210bb9", "Product mark changed")
    for name, expected in LEGAL_CORE_HASHES.items():
        raw = (ROOT/name).read_text(encoding="utf-8")
        # Only the reviewed website-purpose paragraph is excluded. The rest of
        # each legal panel must match its pre-refresh normalized bytes.
        check(legal_core(raw,name)==expected, "Legal/processing content changed: "+name)
        check("Unternehmensauftritt" in raw and "DigitalArtDeco" in raw, "Legal branding missing")
    legal = Page((ROOT/"impressum.html").read_text(encoding="utf-8")).text
    for value in [OWNER,"Sperberweg 27","86609 Donauwörth","Geschäftsführer Harun Aktas",
                  "Amtsgericht Augsburg","HRB 43034","USt-IdNr.: DE464701318",
                  "info@dadlabs.de","+49 176 48296275"]:
        check(value in legal, "Verified legal fact missing: "+value)
    check("1260195" not in legal, "Disallowed register identifier")
    legal_translation_audit((ROOT / "impressum.html").read_text(encoding="utf-8"),
                            (ROOT / "legal-notice.html").read_text(encoding="utf-8"))

    manifest = json.loads((ROOT/CURRENT_DIR/"manifest.json").read_text(encoding="utf-8"))
    recipe = json.loads((ROOT/CURRENT_DIR/"source-selection.json").read_text(encoding="utf-8"))
    check(manifest["date"]==recipe["date"]=="2026-09-09", "Current selection date")
    check([e["id"] for e in manifest["captures"]]==list(CURRENT_APPROVED), "Five-view selection/order")
    check([e["id"] for e in recipe["sources"]]==list(CURRENT_APPROVED), "Recipe selection")
    check("no resampling" in manifest["processing"] and "not a field at a plot marker frequency" in manifest["context"], "Processing/context boundary missing")
    allowed_images, current_copy = set(), {}
    for item, source in zip(manifest["captures"],recipe["sources"]):
        expected=CURRENT_APPROVED[item["id"]]
        for key,value in expected.items():
            check(item.get(key)==value, "Approved image identity changed: "+item["id"]+"/"+key)
            if key in source: check(source[key]==value, "Preparation recipe changed: "+key)
        for key,value in source.items(): check(item.get(key)==value, "Manifest/recipe mismatch")
        check(item["derivative"]==item["id"]+".png" and item["detail"]=="views/"+item["id"]+".html", "Unexpected derivative route")
        rel=CURRENT_DIR+"/"+item["derivative"]
        allowed_images.add(rel)
        png=read_png(ROOT/rel)
        check(sha(ROOT/rel)==item["sha256"] and (ROOT/rel).stat().st_size==item["bytes"], "PNG file identity: "+rel)
        check(png["rgba_pixel_sha256"]==item["rgba_sha256"], "PNG pixel identity: "+rel)
        check((png["width"],png["height"])==(item["width"],item["height"]), "PNG dimensions: "+rel)
        check(set(png["chunks"])=={"IHDR","IDAT","IEND"}, "PNG metadata: "+rel)
        check(all(item.get(k) for k in ["caption","alt","title","use","group"]), "Missing image description")
        current_copy[item["id"]]=item
    check({p.relative_to(ROOT).as_posix() for p in (ROOT/CURRENT_DIR).glob("*.png")}==allowed_images, "Unapproved current PNG")

    active = ACTIVE + SOLVER_PAGES + REFRESH_PAGES + ["views/"+key+".html" for key in CURRENT_APPROVED] + ["docs/"+key+".html" for key in CURRENT_NOTES] + ["docs/index.html"]
    for rel in active:
        text=(ROOT/rel).read_text(encoding="utf-8")
        check(not re.search(r"[\u2013\u2014]|&(?:ndash|mdash);",text), "En/em dash: "+rel)
        check(not unsupported(text), "Unsupported positive claim in "+rel+": "+str(unsupported(text)))
        check(not PRIVATE_COMMIT_HASH_PATTERN.search(text), "Private commit-like ID in active text: "+rel)
        check(not re.search(r"\b(?:Sonnet|HFSS|CST|COMSOL)\b",Page(text).text if rel.endswith(".html") else text,re.I), "Competitor in new copy: "+rel)
        check("canonical-yee/" not in text and ASSET_DIR+"/" not in text, "Historical image in current presentation: "+rel)
    check(not unsupported("Not externally validated. Not production-ready. Not released for production use."), "Negated-claim regression")
    check(len(unsupported("Externally validated and production-ready."))==2, "Positive-claim regression")

    for rel in paths:
        p=ROOT/rel
        check(not p.is_symlink(), "Public filesystem link: "+rel)
        check(p.suffix.lower() not in FORBIDDEN_SUFFIXES, "Private code/binary/archive: "+rel)
        check(not any(part.lower() in {"references_local","private","internal","_incoming",".local_temp",".local_private_assets"} for part in p.relative_to(ROOT).parts), "Private publication path: "+rel)
        if p.is_file() and (p.suffix.lower() in TEXT_SUFFIXES or p.name=="CNAME"):
            text=p.read_text(encoding="utf-8",errors="replace")
            for label,pattern in [("private path",PRIVATE_PATH_PATTERN),("internal identifier",INTERNAL_IDENTIFIER_PATTERN),("private context",PRIVATE_CONTEXT_PATTERN),("tracking",TRACKING_PATTERN),("credential",TOKEN_PATTERN)]:
                check(not pattern.search(text), label+" in public text: "+rel)
    changed=set(git("diff","HEAD","--name-only").splitlines())|set(git("ls-files","--others","--exclude-standard").splitlines())
    allowed_changes=set(ACTIVE+NEW_DOCS+[
        ".gitignore","styles.css","impressum.html","legal-notice.html","datenschutz.html",
        "scripts/validate_native_workbench_preview.py","scripts/prepare_company_screenshots.py","scripts/render_public_notes.py",
        CURRENT_DIR+"/manifest.json",CURRENT_DIR+"/source-selection.json","docs/index.html",
        "assets/brand/README.md","assets/brand/blue_field_sculpture_manifest.json", "favicon.ico", "assets/brand/legacy_kernel_wave_favicon.ico"
    ])|allowed_images|set(BRAND_IMAGES)|{"views/"+key+".html" for key in list(CURRENT_APPROVED)+LEGACY_VIEWS}|{"docs/"+key+".html" for key in CURRENT_NOTES}
    allowed_changes |= set(SOLVER_PAGES) | solver_images | {SOLVER_DIR + "/manifest.json"}
    allowed_changes |= set(REFRESH_PAGES) | refresh_images | {REFRESH_DIR + "/manifest.json",
        REFRESH_DIR + "/source-selection.json", "docs/company_screenshot_provenance_2026_09_09.md"}
    check(changed<=allowed_changes,"Changes outside website allowlist: "+str(sorted(changed-allowed_changes)))
    for rel in changed|set(git("diff","--cached","--name-only").splitlines()):
        check(Path(rel).name not in {e["original"] for e in list(CURRENT_APPROVED.values()) + list(REFRESH_APPROVED.values())}, "Raw source published: "+rel)
        if Path(rel).suffix.lower() in SCIENTIFIC_IMAGE_SUFFIXES:
            check(rel in allowed_images or rel in BRAND_IMAGES or rel in solver_images or rel in refresh_images,"Unapproved image change: "+rel)

    html_count=image_count=0
    for rel in paths:
        if not rel.endswith(".html"): continue
        p=ROOT/rel
        raw=p.read_text(encoding="utf-8")
        page=Page(raw); html_count+=1
        for href in page.hrefs: link_check(p,href)
        for resource in page.resources: link_check(p,resource,True)
        for a in page.images:
            image_count+=1
            check("alt" in a and (a["alt"] or "assets/brand/" in a.get("src","")), "Missing descriptive alt: "+rel)
            check(a.get("width","").isdigit() and a.get("height","").isdigit(), "Missing image dimensions: "+rel)
            if "assets/brand/" not in a.get("src",""):
                target,_=local_target(p,a["src"])
                check(target.relative_to(ROOT).as_posix() in allowed_images | solver_images | refresh_images, "Old or unapproved active image: "+rel)
        check(sum(t=="h1" for t,_ in page.tags)==1,"Expected one H1: "+rel)
        lang="de" if rel in {"impressum.html","datenschutz.html"} else "en"
        check(any(t=="html" and a.get("lang")==lang for t,a in page.tags),"Language missing: "+rel)
        check(page.metas.get("description"),"Meta description missing: "+rel)
        legal_footer_audit(raw, rel)
        if rel not in {"impressum.html", "legal-notice.html", "datenschutz.html"}:
            header = Page(re.search(r'<header[^>]*>([\s\S]*?)</header>', raw).group(1))
            check((ROOT / "solver-development.html").resolve() in {local_target(p, h)[0] for h in header.hrefs},
                  "Solver Development navigation missing: " + rel)
        if rel.startswith("views/"): check(NOTICE in page.text,"Detail preview boundary missing: "+rel)
        if rel.startswith("docs/"):
            check('class="docs-page"' in raw and "DigitalArtDeco" in page.text,"Styled documentation missing: "+rel)

    raw_home=(ROOT/"index.html").read_text(encoding="utf-8")
    home=Page(raw_home)
    brand_views=[a for a in home.images if "assets/brand/" in a.get("src","")]
    check(len(brand_views)==2 and all(a.get("src")=="assets/brand/dad_fieldworks_blue_field_sculpture-256.png" for a in brand_views), "Current header/product illustration missing")
    check(any("rather than simulation data" in a.get("alt","") for a in brand_views), "Brand artwork must be distinguished from data")
    check({"company","focus","fieldworks","outlook","contact","main-content"}<=home.ids,"Company anchors missing")
    captures=[a for a in home.images if CURRENT_DIR in a["src"] or REFRESH_DIR in a["src"]]
    active_images = {CURRENT_DIR + "/" + key + ".png" for key in ["rf-sketcher", "cartesian-s-parameters"]}
    active_images |= {REFRESH_DIR + "/" + e.get("preview", e)["derivative"] for e in refresh_copy.values()}
    check(len(captures)==7 and {a["src"] for a in captures}==active_images,"Exact current gallery missing")
    check(all(a.get("loading")=="lazy" for a in captures),"Below-fold images should lazy-load")
    social=refresh_copy["hy-longitudinal"]
    check(home.metas.get("og:image")==home.metas.get("twitter:image")=="https://www.dadlabs.de/"+REFRESH_DIR+"/hy-longitudinal-preview.png","Stale social image")
    check(home.metas.get("og:image:width")=="1412" and home.metas.get("og:image:height")=="481","Social dimensions")
    check(home.metas.get("og:image:alt")==home.metas.get("twitter:image:alt")==social["alt"],"Social image description")
    title="DigitalArtDeco Labs | Electromagnetic Simulation Software"
    check(home.metas.get("og:title")==home.metas.get("twitter:title")==title and "<title>"+title+"</title>" in raw_home,"Company metadata title")
    check(home.metas.get("description")==home.metas.get("og:description")==home.metas.get("twitter:description") and "DigitalArtDeco Labs develops" in home.metas["description"],"Company descriptions")
    check(home.metas.get("og:site_name")=="DigitalArtDeco Labs","Company site name")
    check([a.get("href") for t,a in home.tags if t=="link" and a.get("rel")=="canonical"]==["https://www.dadlabs.de/"],"Canonical domain")
    check(home.metas.get("og:url")=="https://www.dadlabs.de/","OG domain")
    check(not any(h.endswith(".md") for h in home.hrefs),"Homepage should use styled documentation")
    for item in current_copy.values():
        # The superseded Smith page is checked against its new image above.
        # Other earlier detail pages retain their original content and assets.
        if item["id"] == "smith-chart":
            continue
        link=item["detail"]
        retained = item["id"] in {"rf-sketcher", "cartesian-s-parameters"}
        check((link in home.hrefs) == retained,"Incorrect current/historical image link: "+link)
        raw=(ROOT/link).read_text(encoding="utf-8"); detail=Page(raw)
        facts={
            "pcb-geometry": ["Tuto construction", "not a simulation result", "excludes the private project path"],
            "rf-sketcher": ["Tuto construction", "40 mm by 20 mm", "constraints are not evaluated", "no results"],
            "cartesian-s-parameters": ["linear magnitude, not dB", "S(1,1)", "S(1,2)", "S(2,1)", "S(2,2)", "1.700 GHz"],
            "smith-chart": ["S(2,2)", "2.800 GHz", "Gamma", "50 ohm reference", "not a measurement"],
            "magnetic-field": ["H_z in A/m", "step 12288", "3.071875e-09 s", "Z slice 16", "not a field at"]
        }
        check(all(fact in detail.text for fact in facts[item["id"]]), "Scientific detail boundary changed: "+item["id"])
        full=CURRENT_DIR+"/"+item["derivative"]
        check("../"+full in detail.hrefs,"Full-resolution link missing")
        check([a.get("href") for t,a in detail.tags if t=="link" and a.get("rel")=="canonical"]==["https://www.dadlabs.de/"+link],"Detail canonical")
        for name,page,prefix in [("home",home,""),("detail",detail,"../")]:
            if name == "home" and not retained:
                continue
            figures=[f for f in page.figures if any(a.get("src")==prefix+full for a in f["images"])]
            check(len(figures)==1,"Figure missing/duplicated: "+name+"/"+item["id"])
            if figures:
                image=figures[0]["images"][0]
                check(image.get("alt")==item["alt"] and image.get("width")==str(item["width"]) and image.get("height")==str(item["height"]),"Figure description/dimensions: "+item["id"])
                check(item["caption"] in " ".join(figures[0]["data"]),"Incorrect figure caption: "+item["id"])
    org=json.loads(re.search(r'<script type="application/ld\+json">\s*([\s\S]*?)</script>',raw_home).group(1))
    check(org.get("@type")=="Organization" and org.get("name")==OWNER and org.get("legalName")==OWNER,"Organization identity")
    check(org.get("url")=="https://www.dadlabs.de/" and org.get("@id")=="https://www.dadlabs.de/#organization","Organization domain")
    check(org.get("brand")=={"@type":"Brand","name":"DAD FieldWorks"} and "logo" not in org,"Product symbol must not become company logo")
    check(org.get("email")=="info@dadlabs.de" and org.get("telephone")=="+4917648296275","Organization contact")
    check(org.get("address")=={"@type":"PostalAddress","streetAddress":"Sperberweg 27","postalCode":"86609","addressLocality":"Donauwörth","addressCountry":"Deutschland"},"Organization address")
    for stem in CURRENT_NOTES:
        source=(ROOT/"docs"/(stem+".md")).read_text(encoding="utf-8")
        page=Page((ROOT/"docs"/(stem+".html")).read_text(encoding="utf-8"))
        check(NOTICE in page.text or stem=="publication_notes","Technical preview boundary lost")
        document_source_audit(source,page.text,stem)
    for rel in ACTIVE+NEW_DOCS:
        p=ROOT/rel
        if p.suffix==".md":
            for href in re.findall(r"\]\(([^)\s]+)(?:\s+[^)]*)?\)",p.read_text(encoding="utf-8")): link_check(p,href)
    css=(ROOT/"styles.css").read_text(encoding="utf-8")
    check(not re.search(r"(?i)(?:@import\s+|url\(\s*)['\"]?(?:https?:)?//",css),"External CSS/font dependency")
    check(all(s in css for s in [".result-gallery",".docs-page","height: auto",":focus-visible","@media (max-width: 720px)","grid-template-columns: 1fr"]),"Responsive/focus contract")
    for url in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)",css): link_check(ROOT/"styles.css",url,True)
    check("Historical" in (ROOT/"assets/asset_manifest.md").read_text(encoding="utf-8"),"Historical inventory label")
    check("Historical visual records" in (ROOT/"docs/README.md").read_text(encoding="utf-8"),"Historical notes label")
    diff=subprocess.run(["git","diff","--check"],cwd=ROOT,capture_output=True,text=True,env={**os.environ,"GIT_OPTIONAL_LOCKS":"0"})
    check(diff.returncode==0,"Whitespace check: "+diff.stdout)
    audit=copy_quality_audit(raw_home)
    return {"status":"PASS" if not FAILURES else "FAIL","current_captures":len(refresh_copy)+2,
            "new_captures":len(refresh_copy), "new_pngs":len(refresh_images),
            "new_png_bytes":sum((ROOT / p).stat().st_size for p in refresh_images),
            "retained_september_9_png_bytes":sum(e["bytes"] for e in current_copy.values()),"historical":historical,
            "protected_files":len(PROTECTED),"legal_core_checks":len(LEGAL_CORE_HASHES),
            "solver_development":solver_report,
            "html_pages":html_count,"html_images":image_count,"public_files_scanned":len(paths),
            "changed_paths":sorted(changed),"copy_audit":audit,"failures":FAILURES,
            "private_writes":0,"solver_runs":0,"network_requests":0}

if __name__=="__main__":
    try:
        result=validate()
    except Exception as error:
        result={"status":"FAIL","error":str(error),"failures":FAILURES}
    print(json.dumps(result,indent=2,ensure_ascii=True))
    sys.exit(0 if result["status"]=="PASS" else 1)
