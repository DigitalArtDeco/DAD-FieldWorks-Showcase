#!/usr/bin/env python3
"""Validate the public native Workbench screenshot publication tranche.

This validator is intentionally standard-library only. It checks the bounded
static-site, image, provenance, link, and public-safety contract without
reaching external services.
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
SCREENSHOT_DIR = ROOT / "assets" / "screenshots" / "native_workbench_preview"
MANIFEST_PATH = SCREENSHOT_DIR / "manifest.json"

EXPECTED_ASSETS = {
    "dad_fieldworks_native_workbench_scalar_slice_synthetic.png": (1440, 861),
    "dad_fieldworks_native_workbench_pcb_cross_section.png": (1440, 861),
    "dad_fieldworks_native_workbench_vector_glyphs_synthetic.png": (1439, 861),
    "dad_fieldworks_native_workbench_claim_aware_report.png": (1440, 861),
}

EXPECTED_SOURCES = {
    "dad_fieldworks_native_workbench_scalar_slice_synthetic.png": "Screenshot 2026-08-08 144237.png.png",
    "dad_fieldworks_native_workbench_pcb_cross_section.png": "Screenshot 2026-08-08 144220.png.png",
    "dad_fieldworks_native_workbench_vector_glyphs_synthetic.png": "Screenshot 2026-08-08 144313.png.png",
    "dad_fieldworks_native_workbench_claim_aware_report.png": "Screenshot 2026-08-08 144200.png.png",
}

COPYRIGHT_NOTICE = "Copyright © 2026 Harun Aktas. All rights reserved."

REQUIRED_ASSET_KEYS = {
    "AssetId",
    "FileName",
    "RelativePath",
    "SourceBasename",
    "AssetType",
    "VisualRole",
    "Width",
    "Height",
    "ByteCount",
    "Sha256",
    "PixelFormat",
    "MetadataStrippedQ",
    "PublicSafetyReviewQ",
    "SyntheticFixtureQ",
    "PhysicalSolverResultClaimQ",
    "ExternalValidationClaimQ",
    "ProductionReadinessClaimQ",
    "CommercialSolverEquivalenceClaimQ",
    "CopyrightHolder",
    "CopyrightNotice",
    "Caption",
    "AltText",
}

TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".txt", ".xml", ".yml", ".yaml"}
# SHA-256 values keep prohibited identifiers and claim phrases out of the
# public validator itself. Text is tokenized and compared by digest below.
EMPLOYER_CUSTOMER_TOKEN_DIGESTS = {
    "36aa04f4333ebc94260a496b27815226e288d9f946e5eca92362e42c09626290",
    "423d16ce8c066ceb5714dbb2f9d16eaa59e3571d0318367039755e7e64ceb32f",
}
FORBIDDEN_NGRAM_DIGESTS = {
    1: {
        "1b360196d74d67963a9cc722a353b918cfcb29f192a9b9fbb6c5148145128dee",
        "9093e3e8da3a29753bcd93ee403878e72a5e4e9cc05119f2cfcc6a4052d95dda",
        "1cedb4f23a2f919d91ca0de560dd76c5255253dd67946ff70426f8b265a27ca8",
        "6881efc899e97d9e1e5f13239cf82d441e669b4f78b79d3fe25b86e82874e015",
    },
    2: {
        "3f225a4b89f0f01dd501c9347a25bfa2e451c2881545f9c52d014c5bf75ebd49",
        "b208890d046906f486de3091cbc45cefc9d76eb922bb3c00eceff22d615ae358",
        "444c002cd33776bc11653d63d3dce050bfc1d7aed363481ed176931a7b64405d",
        "b69f8e2d9459c35af2dcebdba3ba023689f11e429e0a2ac46e243c982be51a35",
    },
    4: {
        "14e643657eae1cecf1095160c63c76c057eaf0e45cd23a5013ddccb13788d101",
    },
}
PRIVATE_PATH_PATTERN = re.compile(
    r"(?i)(?:(?<![a-z0-9+.-])[a-z]:[\\/]|file://|\\\\)[^\s<>'\"]+"
)
TRACKING_PATTERN = re.compile(
    r"(?i)(google-analytics|googletagmanager|gtag\s*\(|matomo|plausible\.io|segment\.com|mixpanel|hotjar|dataLayer\s*=)"
)
TOKEN_PATTERN = re.compile(r"[a-z0-9_]+(?:-[a-z0-9_]+)*")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.scripts: list[str] = []
        self.meta: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self._inside_workbench = False
        self._anchor_depth = 0
        self.workbench_figures = 0
        self.workbench_captions = 0
        self.workbench_images: list[dict[str, str | None]] = []

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str | None]:
        return {key.lower(): value for key, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = self._attrs(attrs)
        if value := data.get("id"):
            self.ids.append(value)
        if tag == "section" and data.get("id") == "workbench":
            self._inside_workbench = True
        if tag == "a":
            self._anchor_depth += 1
            if href := data.get("href"):
                self.hrefs.append(href)
        elif tag == "img":
            record = {
                "src": data.get("src"),
                "alt": data.get("alt"),
                "width": data.get("width"),
                "height": data.get("height"),
                "loading": data.get("loading"),
                "decoding": data.get("decoding"),
                "linked": "true" if self._anchor_depth else "false",
            }
            self.images.append(record)
            if self._inside_workbench:
                self.workbench_images.append(record)
        elif tag == "figure" and self._inside_workbench:
            self.workbench_figures += 1
        elif tag == "figcaption" and self._inside_workbench:
            self.workbench_captions += 1
        elif tag == "script":
            if src := data.get("src"):
                self.scripts.append(src)
        elif tag == "meta":
            self.meta.append(data)
        elif tag == "link":
            self.links.append(data)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._anchor_depth:
            self._anchor_depth -= 1
        if tag == "section" and self._inside_workbench:
            self._inside_workbench = False


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def read_png(path: Path) -> tuple[int, int, int, int, list[str]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("invalid PNG signature")
    offset = 8
    chunks: list[str] = []
    width = height = bit_depth = color_type = -1
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("truncated PNG chunk")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        stored_crc = struct.unpack(">I", data[offset + 8 + length : offset + 12 + length])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(chunk_data, actual_crc) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise ValueError(f"CRC mismatch in {chunk_type.decode('ascii', 'replace')}")
        name = chunk_type.decode("ascii")
        chunks.append(name)
        if name == "IHDR":
            if length != 13:
                raise ValueError("invalid IHDR length")
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk_data[:10])
        offset += 12 + length
        if name == "IEND":
            break
    if offset != len(data):
        raise ValueError("trailing bytes after IEND")
    if chunks[:1] != ["IHDR"] or "IDAT" not in chunks or chunks[-1:] != ["IEND"]:
        raise ValueError("missing or misplaced critical PNG chunks")
    return width, height, bit_depth, color_type, chunks


def local_target_exists(source_file: Path, target: str) -> bool:
    parts = urlsplit(target)
    if parts.scheme or target.startswith(("//", "mailto:", "tel:")):
        return True
    if not parts.path:
        return True
    candidate = (source_file.parent / unquote(parts.path)).resolve()
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


def staged_raw_incoming_paths() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    paths = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    return [
        path
        for path in paths
        if path.startswith("_incoming/")
        or re.search(r"(?i)(?:^|/)Screenshot 2026-08-08 144(?:200|220|237|313)\.png(?:\.png)?$", path)
    ]


def validate() -> list[str]:
    failures: list[str] = []
    if not MANIFEST_PATH.is_file():
        return [f"missing screenshot manifest: {MANIFEST_PATH.relative_to(ROOT)}"]

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"manifest is not valid UTF-8 JSON: {exc}"]

    required_top = {
        "SchemaId",
        "SchemaVersion",
        "GeneratedAtUtc",
        "CopyrightHolder",
        "CopyrightNotice",
        "PublicProject",
        "Application",
        "SourceClass",
        "ClaimBoundary",
        "Assets",
    }
    missing_top = sorted(required_top - manifest.keys())
    if missing_top:
        fail(failures, f"manifest missing top-level keys: {', '.join(missing_top)}")
    if manifest.get("SchemaId") != "DAD_PUBLIC_NATIVE_WORKBENCH_SCREENSHOT_MANIFEST_V1":
        fail(failures, "manifest SchemaId mismatch")
    if manifest.get("SchemaVersion") != 1:
        fail(failures, "manifest SchemaVersion must be 1")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(manifest.get("GeneratedAtUtc", ""))):
        fail(failures, "manifest GeneratedAtUtc must be a UTC second-precision timestamp")
    if manifest.get("CopyrightHolder") != "Harun Aktas":
        fail(failures, "manifest copyright holder mismatch")
    if manifest.get("CopyrightNotice") != COPYRIGHT_NOTICE:
        fail(failures, "manifest copyright notice mismatch")

    assets = manifest.get("Assets")
    if not isinstance(assets, list):
        fail(failures, "manifest Assets must be an array")
        assets = []
    if len(assets) != 4:
        fail(failures, f"manifest must contain 4 assets, found {len(assets)}")

    records: dict[str, dict[str, object]] = {}
    for index, record in enumerate(assets):
        if not isinstance(record, dict):
            fail(failures, f"asset record {index} is not an object")
            continue
        missing = sorted(REQUIRED_ASSET_KEYS - record.keys())
        if missing:
            fail(failures, f"asset record {index} missing keys: {', '.join(missing)}")
        filename = record.get("FileName")
        if not isinstance(filename, str):
            fail(failures, f"asset record {index} has no valid FileName")
            continue
        if filename in records:
            fail(failures, f"duplicate manifest FileName: {filename}")
        records[filename] = record

    if set(records) != set(EXPECTED_ASSETS):
        fail(failures, "manifest filenames do not match the four stable public filenames")

    metadata_chunk_count = 0
    for filename, expected_dimensions in EXPECTED_ASSETS.items():
        path = SCREENSHOT_DIR / filename
        record = records.get(filename, {})
        if not path.is_file():
            fail(failures, f"missing public screenshot: {path.relative_to(ROOT)}")
            continue
        try:
            width, height, bit_depth, color_type, chunks = read_png(path)
        except (OSError, ValueError, UnicodeError) as exc:
            fail(failures, f"{filename} does not decode as a structurally valid PNG: {exc}")
            continue
        if (width, height) != expected_dimensions:
            fail(failures, f"{filename} dimensions {(width, height)} != {expected_dimensions}")
        if bit_depth != 8 or color_type not in {2, 6}:
            fail(failures, f"{filename} must be 8-bit RGB or RGBA, got depth={bit_depth}, type={color_type}")
        ancillary = [chunk for chunk in chunks if chunk not in {"IHDR", "IDAT", "IEND"}]
        metadata_chunk_count += len(ancillary)
        if ancillary:
            fail(failures, f"{filename} contains ancillary metadata chunks: {', '.join(ancillary)}")
        size = path.stat().st_size
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        relative = path.relative_to(ROOT).as_posix()
        if record.get("RelativePath") != relative:
            fail(failures, f"{filename} RelativePath mismatch")
        if record.get("SourceBasename") != EXPECTED_SOURCES[filename]:
            fail(failures, f"{filename} SourceBasename mismatch")
        if record.get("AssetType") != "application screenshot":
            fail(failures, f"{filename} AssetType mismatch")
        if record.get("Width") != width or record.get("Height") != height:
            fail(failures, f"{filename} manifest dimensions mismatch")
        if record.get("ByteCount") != size:
            fail(failures, f"{filename} manifest byte count mismatch")
        if str(record.get("Sha256", "")).lower() != digest:
            fail(failures, f"{filename} manifest SHA-256 mismatch")
        for key in ("MetadataStrippedQ", "PublicSafetyReviewQ", "SyntheticFixtureQ"):
            if record.get(key) is not True:
                fail(failures, f"{filename} {key} must be true")
        for key in (
            "PhysicalSolverResultClaimQ",
            "ExternalValidationClaimQ",
            "ProductionReadinessClaimQ",
            "CommercialSolverEquivalenceClaimQ",
        ):
            if record.get(key) is not False:
                fail(failures, f"{filename} {key} must be false")
        if not str(record.get("AltText", "")).strip():
            fail(failures, f"{filename} manifest AltText is empty")
        if not str(record.get("Caption", "")).strip():
            fail(failures, f"{filename} manifest Caption is empty")
        if record.get("CopyrightHolder") != "Harun Aktas" or record.get("CopyrightNotice") != COPYRIGHT_NOTICE:
            fail(failures, f"{filename} copyright fields mismatch")

    index_path = ROOT / "index.html"
    readme_path = ROOT / "README.md"
    index_text = index_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(index_text)

    duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicates:
        fail(failures, f"duplicate HTML ids: {', '.join(duplicates)}")
    if "workbench" not in parser.ids:
        fail(failures, "index.html is missing id=workbench")
    if "From PCB cross-section to scientific 3D field inspection." not in index_text:
        fail(failures, "index.html is missing the required Workbench heading")
    if "Independent R&amp;D prototype &middot; Synthetic visualization fixtures" not in index_text and \
       "Independent R&D prototype · Synthetic visualization fixtures" not in index_text:
        fail(failures, "index.html is missing the visible Workbench badge")
    if parser.workbench_figures != 4 or parser.workbench_captions != 4:
        fail(
            failures,
            f"Workbench gallery must have 4 figures and 4 captions; found {parser.workbench_figures}/{parser.workbench_captions}",
        )
    if len(parser.workbench_images) != 4:
        fail(failures, f"Workbench gallery must have 4 images; found {len(parser.workbench_images)}")
    else:
        for index, image in enumerate(parser.workbench_images):
            src = image.get("src") or ""
            if Path(src).name not in EXPECTED_ASSETS:
                fail(failures, f"unexpected Workbench image source: {src}")
            if not (image.get("alt") or "").strip():
                fail(failures, f"Workbench image {index + 1} is missing useful alt text")
            if not image.get("width") or not image.get("height"):
                fail(failures, f"Workbench image {index + 1} is missing width/height")
            if image.get("decoding") != "async":
                fail(failures, f"Workbench image {index + 1} must use decoding=async")
            if index > 0 and image.get("loading") != "lazy":
                fail(failures, f"Workbench image {index + 1} must use loading=lazy")
            if image.get("linked") != "true":
                fail(failures, f"Workbench image {index + 1} must link to the full-resolution PNG")

    for image in parser.images:
        src = image.get("src") or ""
        if not src or not local_target_exists(index_path, src):
            fail(failures, f"missing index.html image target: {src or '<empty>'}")
        if not (image.get("alt") or "").strip():
            fail(failures, f"index.html image has empty alt text: {src}")

    for href in parser.hrefs:
        if not local_target_exists(index_path, href):
            fail(failures, f"missing index.html link target: {href}")
        parts = urlsplit(href)
        if parts.fragment and not parts.scheme and not parts.path and parts.fragment not in parser.ids:
            fail(failures, f"unresolved homepage fragment: #{parts.fragment}")

    for src in parser.scripts:
        if urlsplit(src).scheme or src.startswith("//"):
            fail(failures, f"external JavaScript dependency: {src}")
        elif not local_target_exists(index_path, src):
            fail(failures, f"missing local JavaScript dependency: {src}")

    canonical = [item.get("href") for item in parser.links if item.get("rel") == "canonical"]
    if canonical != ["https://www.dadlabs.de/"]:
        fail(failures, "canonical URL must be exactly https://www.dadlabs.de/")
    meta_lookup: dict[tuple[str, str], str | None] = {}
    for item in parser.meta:
        if item.get("property"):
            meta_lookup[("property", item["property"] or "")] = item.get("content")
        if item.get("name"):
            meta_lookup[("name", item["name"] or "")] = item.get("content")
    expected_meta = {
        ("property", "og:type"): "website",
        ("property", "og:title"): "DAD FieldWorks — Native PCB EM Workbench Development Preview",
        ("property", "og:image"): "https://www.dadlabs.de/assets/screenshots/native_workbench_preview/dad_fieldworks_native_workbench_scalar_slice_synthetic.png",
        ("property", "og:image:width"): "1440",
        ("property", "og:image:height"): "861",
        ("name", "twitter:card"): "summary_large_image",
    }
    for key, expected in expected_meta.items():
        if meta_lookup.get(key) != expected:
            fail(failures, f"metadata mismatch for {key[1]}")

    markdown_targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", readme_text)
    for target in markdown_targets:
        clean_target = target.strip().split(maxsplit=1)[0].strip("<>")
        if not local_target_exists(readme_path, clean_target):
            fail(failures, f"missing README link/image target: {clean_target}")
    for filename in EXPECTED_ASSETS:
        relative = f"assets/screenshots/native_workbench_preview/{filename}"
        if readme_text.count(relative) < 2:
            fail(failures, f"README image is not clickable to its full-size asset: {relative}")

    required_links = (
        "assets/screenshots/native_workbench_preview/manifest.json",
        "docs/native_workbench_development_preview_provenance.md",
    )
    for required in required_links:
        if required not in index_text:
            fail(failures, f"index.html missing technical-material link: {required}")
        if required not in readme_text:
            fail(failures, f"README missing technical-material link: {required}")
        if not (ROOT / required).is_file():
            fail(failures, f"technical-material target does not exist: {required}")

    css_text = (ROOT / "styles.css").read_text(encoding="utf-8")
    for selector in (
        ".workbench-preview",
        ".workbench-gallery",
        ".workbench-card",
        ".workbench-card-featured",
        ".workbench-claim-note",
        ".workbench-badge",
    ):
        if selector not in css_text:
            fail(failures, f"styles.css missing Workbench selector: {selector}")
    if "@media" not in css_text or "object-fit: contain" not in css_text:
        fail(failures, "styles.css lacks required responsive image treatment")

    all_public_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in iter_public_text_files())
    if PRIVATE_PATH_PATTERN.search(all_public_text):
        fail(failures, "an absolute Windows/UNC path appears in public text files")
    lowered = all_public_text.lower()
    tokens = TOKEN_PATTERN.findall(lowered)
    employer_customer_count = sum(
        hashlib.sha256(token.encode("utf-8")).hexdigest() in EMPLOYER_CUSTOMER_TOKEN_DIGESTS
        for token in tokens
    )
    if employer_customer_count:
        fail(failures, f"employer/customer identifier digest matched {employer_customer_count} time(s) in public text")
    forbidden_phrase_count = 0
    for token_count, digests in FORBIDDEN_NGRAM_DIGESTS.items():
        for index in range(len(tokens) - token_count + 1):
            phrase = " ".join(tokens[index : index + token_count])
            if hashlib.sha256(phrase.encode("utf-8")).hexdigest() in digests:
                forbidden_phrase_count += 1
    if forbidden_phrase_count:
        fail(failures, f"forbidden public phrase digest matched {forbidden_phrase_count} time(s)")
    if TRACKING_PATTERN.search(index_text):
        fail(failures, "tracking or analytics code appears in index.html")

    if (ROOT / "CNAME").read_text(encoding="utf-8").strip() != "www.dadlabs.de":
        fail(failures, "CNAME must remain exactly www.dadlabs.de")
    if not (ROOT / "assets" / "hero" / "pcb2d_microstrip_field_scientific_v2_hero.gif").is_file():
        fail(failures, "required existing hero animation is missing")
    if not (ROOT / "impressum.html").is_file() or not (ROOT / "datenschutz.html").is_file():
        fail(failures, "a required legal page is missing")

    try:
        raw_incoming = staged_raw_incoming_paths()
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        fail(failures, f"could not inspect staged paths: {exc}")
        raw_incoming = []
    if raw_incoming:
        fail(failures, f"raw incoming screenshot staged: {', '.join(raw_incoming)}")

    print(f"PublicScreenshotCount: {len([name for name in EXPECTED_ASSETS if (SCREENSHOT_DIR / name).is_file()])}")
    print(f"BrokenAssetReferenceCount: {sum('missing index.html image target' in item for item in failures)}")
    print(f"BrokenInternalLinkCount: {sum('link target' in item or 'fragment' in item for item in failures)}")
    print(f"MissingAltTextCount: {sum('alt text' in item for item in failures)}")
    print(f"DuplicateHtmlIdCount: {len(duplicates)}")
    print(f"AbsolutePrivatePathCount: {sum('absolute Windows/UNC path' in item for item in failures)}")
    print(f"EmployerCustomerIdentifierCount: {employer_customer_count}")
    print(f"ForbiddenPublicClaimCount: {forbidden_phrase_count}")
    print(f"ExternalJavascriptDependencyCount: {sum('external JavaScript dependency' in item for item in failures)}")
    print(f"TrackingOrAnalyticsCount: {sum('tracking or analytics' in item for item in failures)}")
    print(f"RawIncomingAssetStagedCount: {len(raw_incoming)}")
    print(f"AssetManifestMismatchCount: {sum('manifest' in item.lower() for item in failures)}")
    print(f"AncillaryPngMetadataChunkCount: {metadata_chunk_count}")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("\nVALIDATION FAILED", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("ValidationPassQ: True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
