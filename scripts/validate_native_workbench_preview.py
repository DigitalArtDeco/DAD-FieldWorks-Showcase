#!/usr/bin/env python3
"""Offline public-site validator for the September 2026 native workflow preview.

Retains PNG decoding/CRC validation and public-data guards from the previous
validator. Replaces only the superseded four-frame/copy contract with six
approved screenshots and their documented derivatives. No private imports,
network, file writes, solver calls or application execution.
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
NOTICE = "Development preview. External validation is not yet complete. Not released for production use."
OWNER = "DigitalArtDeco Labs UG (haftungsbeschränkt)"
PROTECTED = {
    "CNAME": "a0fcc58c50dbc063e7b42af68f9dce31ea6448863474fbb7848feae732245b4e",
    "COPYRIGHT.md": "17ef284402988e72a6150331b74e14928f0052f1c160aae9027f515b9f23b624",
    "LICENSE_NOTICE.md": "69a949a8032a3181a9ffaf168d0785610b3bd858549fc28a060033095863b739",
    "assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-02.png": "f7f69083156dff0c9fa094f28b744523630cd580263b0c9ae6a7bc5cb47b200b",
    "assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-03.png": "6bb7ab23ab9386aa42ff96a822d2cd27be25a586e0c1339cf10d1a125f76e729",
    "assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-04.png": "e836192e7a6fdf9a4c28d04f58a02a7b77805f0f7f0da69264eb5c04a280ab8e",
    "assets/images/dad-fieldworks/canonical-yee/canonical-yee-z-slice-frame-05.png": "d4d1702c5c3078daf1336f59421e6de6bad9b0d09f0b5171488305132ae301f3",
    "assets/images/dad-fieldworks/canonical-yee/manifest.json": "d60de43e39de8eef9bd4a31c5584ae9f54490f288f167a37af843f0515015947",
    "datenschutz.html": "8f90de5a0d97827e7b416844aeb32acbdbfde0032a05e294f12a618011e0c01f",
    "docs/canonical_yee_field_visualization_provenance.md": "b4c14064bd1272bfb8d5b507400c39d892c848d2fa645a04b227e404edf4fee1",
    "docs/legal_site_identity_audit.md": "fbb8f102aace809fda29fcfb8a50162bc24750fdadecce746aa02c703983bf4d",
    "impressum.html": "3a04a92a45e28cc32a5346c550ceeb2541c25e2a534dd22768e6d7ae94b58c0e"
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
ACTIVE = ["index.html", "README.md", "docs/current_public_status.md",
          "docs/claim_boundaries.md", "assets/hero/README.md",
          "docs/native_workflow_screenshot_provenance.md"]
NEW_DOCS = ["docs/README.md", "docs/showcase_refresh_2026_09.md"]
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



def validate():
    paths = public_files()
    manifest = json.loads((ROOT / ASSET_DIR / "manifest.json").read_text(encoding="utf-8"))
    check(manifest["owner"] == OWNER, "Screenshot copyright owner changed")
    check(manifest["source_date"] == "2026-09-05", "Capture date changed")
    check(manifest["scientific_content_changed"] is False and manifest["generated_scientific_images"] == 0,
          "Scientific asset processing authority changed")
    check("Not supplied" in manifest["executable_provenance"], "Missing executable provenance boundary")
    check([i["id"] for i in manifest["images"]] == list(APPROVED), "Approved six-view selection/order changed")
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

    for rel, expected in PROTECTED.items():
        check((ROOT / rel).is_file() and sha(ROOT / rel) == expected, "Protected bytes changed: " + rel)
    check((ROOT / "CNAME").read_text().strip() == "www.dadlabs.de", "Public domain changed")
    check(sha(ROOT / "favicon.ico") == "ae41a3988a5e832f30c484765370d6f66da9ae391d7a88b955995fb0b80f71ba", "Unapproved browser icon")
    check(sha(ROOT / "assets/brand/dad_fieldworks_kernel_wave_mark.png") == "410e6874da3d6f37bf02836c2ae107be27489f7db93421fb6a29b91af1210bb9", "Original brand mark changed")
    legal = (ROOT / "impressum.html").read_text(encoding="utf-8")
    check("HRB 43034" in legal and "Amtsgericht Augsburg" in legal and "1260195" not in legal,
          "Verified legal identity not preserved")

    active = ACTIVE + ["views/" + key + ".html" for key in APPROVED]
    for rel in active + NEW_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        check(not re.search(r"[\u2013\u2014]|&(?:ndash|mdash);", text), "En/em dash in new public copy: " + rel)
        check(not unsupported(text), "Unsupported positive claim in " + rel + ": " + str(unsupported(text)))
        check(not PRIVATE_COMMIT_HASH_PATTERN.search(text), "Private commit-like ID in active copy: " + rel)
        check(not ROADMAP_LINK_PATTERN.search(text), "Active roadmap link: " + rel)
        check(not MATHEMATICA_PRODUCT_PATTERN.search(text), "Unsupported product path: " + rel)
        if rel in active:
            check("canonical-yee/" not in text and "canonical-yee-z-slice-frame" not in text,
                  "Active historical image reference: " + rel)

    check(not unsupported("Not externally validated. Not production-ready. Not released for production use."),
          "Negated claim regression")
    check(len(unsupported("Externally validated and production-ready.")) == 2, "Positive claim guard regression")
    for rel in paths:
        p = ROOT / rel
        check(not p.is_symlink(), "Public filesystem link: " + rel)
        if p.suffix.lower() in FORBIDDEN_SUFFIXES:
            check(False, "Private code/binary/archive in public set: " + rel)
        check(not any(part.lower() in {"references_local", "private", "internal", "_incoming", ".local_temp", ".local_private_assets"}
                      for part in p.relative_to(ROOT).parts), "Private/raw publication path: " + rel)
        if p.is_file() and (p.suffix.lower() in TEXT_SUFFIXES or p.name == "CNAME"):
            text = p.read_text(encoding="utf-8", errors="replace")
            for label, pattern in [("private path", PRIVATE_PATH_PATTERN), ("internal identifier", INTERNAL_IDENTIFIER_PATTERN),
                                   ("private context", PRIVATE_CONTEXT_PATTERN), ("tracking", TRACKING_PATTERN),
                                   ("credential", TOKEN_PATTERN)]:
                check(not pattern.search(text), label + " in public text: " + rel)
    changed = set(git("diff", "HEAD", "--name-only").splitlines()) | set(git("ls-files", "--others", "--exclude-standard").splitlines())
    allowed_changes = set(ACTIVE + NEW_DOCS + [".gitignore", "styles.css", "favicon.ico", "assets/asset_manifest.md",
                    "scripts/prepare_showcase_screenshots.py", "scripts/validate_native_workbench_preview.py",
                    ASSET_DIR + "/manifest.json"]) | allowed_images | {"views/" + key + ".html" for key in APPROVED}
    check(changed <= allowed_changes, "Changes outside allowlist: " + str(sorted(changed - allowed_changes)))
    source_names = {a["source"].lower() for a in APPROVED.values()} | {"source-manifest.json", "screenshot (8).png", "screenshot (11).png"}
    for rel in changed | set(git("diff", "--cached", "--name-only").splitlines()):
        check(Path(rel).name.lower() not in source_names, "Raw original staged/published: " + rel)
        if Path(rel).suffix.lower() in SCIENTIFIC_IMAGE_SUFFIXES:
            check(rel in allowed_images, "Unapproved new/changed scientific image: " + rel)

    html_count = image_count = 0
    for rel in paths:
        if not rel.endswith(".html"):
            continue
        p = ROOT / rel
        parser = Page(p.read_text(encoding="utf-8"))
        html_count += 1
        for href in parser.hrefs:
            link_check(p, href)
        for resource in parser.resources:
            link_check(p, resource, True)
        for a in parser.images:
            image_count += 1
            check("alt" in a and (a["alt"] or "assets/brand/" in a.get("src", "")), "Missing descriptive alt in " + rel)
            check(a.get("width", "").isdigit() and a.get("height", "").isdigit(), "Missing intrinsic dimensions in " + rel)
        if rel == "index.html" or rel.startswith("views/"):
            check(NOTICE in parser.text, "Visible preview notice missing: " + rel)
            check(sum(tag == "h1" for tag, _ in parser.tags) == 1, "Expected one H1: " + rel)
            check(any(tag == "html" and a.get("lang") == "en" for tag, a in parser.tags), "English language missing")
    home = Page((ROOT / "index.html").read_text(encoding="utf-8"))
    check({"workflow","results","examples","result-context","development","contact","main-content"} <= home.ids, "Workflow anchors missing")
    check("mailto:info@dadlabs.de" in home.hrefs and "tel:+4917648296275" in home.hrefs, "Contact action changed")
    homepage_captures = [a for a in home.images if ASSET_DIR in a["src"]]
    check(len(homepage_captures) == 6 and {a["src"] for a in homepage_captures} == {v["path"] for v in full_images.values()},
          "Expected the exact six distinct homepage captures")
    hero = [a for a in home.images if "simulation-results.png" in a["src"]][0]
    check(hero.get("loading") == "eager" and hero.get("fetchpriority") == "high", "Hero priority regressed")
    check(home.metas.get("og:image") == "https://www.dadlabs.de/" + full_images["simulation-results"]["path"], "Stale social image")
    check(home.metas.get("twitter:image") == home.metas.get("og:image"), "Social images differ")
    check(home.metas.get("og:image:height") == "860", "Social dimensions changed")
    check(home.metas.get("og:image:width") == "1440", "Social width changed")
    hero_alt = manifest["images"][0]["alt"]
    check(home.metas.get("og:image:alt") == home.metas.get("twitter:image:alt") == hero_alt, "Social alt not hero-backed")
    check([a.get("href") for tag, a in home.tags if tag == "link" and a.get("rel") == "canonical"] == ["https://www.dadlabs.de/"], "Homepage canonical URL changed")
    check(home.metas.get("og:url") == "https://www.dadlabs.de/", "Social page URL changed")
    check(home.metas.get("og:title") == home.metas.get("twitter:title") == "DAD FieldWorks | PCB and RF Development Workbench", "Social title mismatch")
    check(home.metas.get("description") == home.metas.get("og:description") == home.metas.get("twitter:description") and "Development preview." in home.metas.get("description", ""), "Description metadata differs or omits preview status")
    for item in manifest["images"]:
        link = "views/" + item["id"] + ".html"
        check(link in home.hrefs, "Missing detail link: " + link)
        detail_text = (ROOT / link).read_text(encoding="utf-8")
        check(item["caption"] in detail_text and item["alt"] in detail_text, "Detail caption/alt not manifest-backed")
        detail = Page(detail_text)
        check([a.get("href") for tag, a in detail.tags if tag == "link" and a.get("rel") == "canonical"] == ["https://www.dadlabs.de/" + link], "Detail canonical URL changed")
        full = full_images[item["id"]]
        check("../" + full["path"] in detail.hrefs, "No full-resolution zoom link")
        for label, page, prefix in [("homepage", home, ""), ("detail", detail, "../")]:
            matches = [fig for fig in page.figures if any(a.get("src") == prefix + full["path"] for a in fig["images"])]
            check(len(matches) == 1, "Missing or duplicated figure on " + label + ": " + item["id"])
            if not matches:
                continue
            figure = matches[0]
            check(len(figure["images"]) == 1, "Unexpected images in figure")
            a = figure["images"][0]
            check(a.get("alt") == item["alt"] and a.get("width") == str(full["width"]) and a.get("height") == str(full["height"]),
                  "Displayed alt/dimensions differ from manifest on " + label + ": " + item["id"])
            text = re.sub(r"\s+", " ", " ".join(figure["data"]))
            check(item["caption"] in text, "Caption belongs to wrong figure on " + label + ": " + item["id"])
            expected_srcset = ", ".join(v["path"] + " " + str(v["width"]) + "w" for v in reversed(item["derivatives"])) if len(item["derivatives"]) > 1 else ""
            check(a.get("srcset", "") == (expected_srcset if label == "homepage" else ""), "Unexpected responsive scientific source")
    raw_home = (ROOT / "index.html").read_text(encoding="utf-8")
    org = json.loads(re.search(r'<script type="application/ld\+json">\s*([\s\S]*?)</script>', raw_home).group(1))
    check(org.get("@type") == "Organization" and org.get("name") == OWNER and org.get("legalName") == OWNER, "Organization identity changed")
    check(org.get("url") == "https://www.dadlabs.de/" and org.get("@id") == "https://www.dadlabs.de/#organization" and org.get("brand") == {"@type":"Brand","name":"DAD FieldWorks"}, "Organization URL or brand changed")
    check(org.get("logo") == "https://www.dadlabs.de/assets/brand/dad_fieldworks_kernel_wave_mark.png", "Organization logo changed")
    check(org.get("email") == "info@dadlabs.de" and org.get("telephone") == "+4917648296275", "Organization contact changed")
    check(org.get("address") == {"@type":"PostalAddress","streetAddress":"Sperberweg 27","postalCode":"86609","addressLocality":"Donauwörth","addressCountry":"Deutschland"}, "Organization address changed")
    for rel in ACTIVE + NEW_DOCS + ["assets/asset_manifest.md"]:
        p = ROOT / rel
        if p.suffix == ".md":
            for href in re.findall(r"\]\(([^)\s]+)(?:\s+[^)]*)?\)", p.read_text(encoding="utf-8")):
                link_check(p, href)
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    check(not re.search(r"(?i)(?:@import\s+|url\(\s*)['\"]?(?:https?:)?//", css), "External CSS/font dependency")
    check(all(s in css for s in [".workflow-showcase", ".result-gallery", "height: auto", ":focus-visible",
                                "@media (max-width: 720px)", "grid-template-columns: 1fr"]), "Responsive/focus contract missing")
    for url in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", css):
        link_check(ROOT / "styles.css", url, True)
    check("Historical" in (ROOT/"assets/asset_manifest.md").read_text(), "Historical inventory context missing")
    check("Historical visual records" in (ROOT/"docs/README.md").read_text(), "Historical documentation context missing")
    diff_check = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True,
                                env={**os.environ, "GIT_OPTIONAL_LOCKS":"0"})
    check(diff_check.returncode == 0, "Whitespace diff check failed: " + diff_check.stdout)
    return {"status": "PASS" if not FAILURES else "FAIL", "approved_captures": len(APPROVED),
            "published_pngs": len(allowed_images), "png_bytes": total_bytes,
            "protected_files": len(PROTECTED), "html_pages": html_count, "html_images": image_count,
            "public_files_scanned": len(paths), "changed_paths": sorted(changed),
            "failures": FAILURES, "private_writes": 0, "solver_runs": 0, "network_requests": 0}

if __name__ == "__main__":
    try:
        result = validate()
    except Exception as error:
        result = {"status":"FAIL", "error": str(error), "failures":FAILURES}
    print(json.dumps(result, indent=2, ensure_ascii=True))
    sys.exit(0 if result["status"] == "PASS" else 1)
