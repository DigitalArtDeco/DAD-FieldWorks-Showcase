"""Package the DAD FDTD ringdown PNG sequence into a compact website GIF."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_DIR = ROOT / "assets" / "animations" / "fdtd_ringdown_png_sequence"
FRAME_DIR = SEQUENCE_DIR / "frames"
METADATA_DIR = SEQUENCE_DIR / "metadata"
MANIFEST_PATH = SEQUENCE_DIR / "manifest.json"
README_PATH = SEQUENCE_DIR / "README.md"

HERO_DIR = ROOT / "assets" / "hero"
GIF_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero.gif"
POSTER_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero_poster.png"
SUMMARY_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero_summary.json"

FPS = 12
GIF_SIZE = (640, 360)
SOURCE_FRAME_SIZE = (720, 405)
SOURCE_GRID_SIZE = (128, 72)
SAMPLE_STEPS = [
    18,
    27,
    36,
    44,
    53,
    62,
    71,
    79,
    88,
    97,
    106,
    114,
    123,
    132,
    141,
    149,
    158,
    167,
    176,
    185,
    193,
    202,
    211,
    220,
    228,
    237,
    246,
    255,
    263,
    272,
    281,
    290,
    299,
    307,
    316,
    325,
    334,
    342,
    351,
    360,
    369,
    377,
    386,
    395,
    404,
    412,
    421,
    430,
]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_frames() -> list[Image.Image]:
    paths = sorted(FRAME_DIR.glob("frame_*.png"))
    if len(paths) != len(SAMPLE_STEPS):
        raise RuntimeError(f"Expected {len(SAMPLE_STEPS)} PNG frames, found {len(paths)}")
    frames: list[Image.Image] = []
    resampling = getattr(Image, "Resampling", Image).LANCZOS
    for path in paths:
        with Image.open(path) as image:
            if image.size != SOURCE_FRAME_SIZE:
                raise RuntimeError(f"Unexpected frame size for {path}: {image.size}")
            frames.append(image.convert("RGB").resize(GIF_SIZE, resampling))
    return frames


def save_optimized_gif(frames: list[Image.Image]) -> None:
    duration_ms = int(round(1000 / FPS))
    palette_frames = [
        frame.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
        for frame in frames
    ]
    palette_frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=palette_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
        disposal=2,
    )


def write_sequence_metadata(frame_count: int) -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    frame_entries = []
    for index, step in enumerate(SAMPLE_STEPS):
        frame_path = FRAME_DIR / f"frame_{index:03d}.png"
        metadata_path = METADATA_DIR / f"frame_{index:03d}.json"
        metadata = {
            "FrameIndex": index,
            "FrameCount": frame_count,
            "ImagePath": relative(frame_path),
            "ImageWidth": SOURCE_FRAME_SIZE[0],
            "ImageHeight": SOURCE_FRAME_SIZE[1],
            "SourceSolver": "DAD FieldWorks 2D TMz FDTD kernel",
            "SourceFieldQuantity": "signed Ez field",
            "RingdownCase": "bounded PEC wall microwave resonator style diagnostic",
            "PecObjectPresentQ": True,
            "CavityDescription": "PEC wall bounded 2D field region with a PEC scatterer mask",
            "SlicePlane": "2D TMz Yee grid",
            "TimeStepOrSampleIndex": step,
            "ColorScaleDescription": "signed cyan orange field color scale with fixed global normalization",
            "NormalizationDescription": "global maximum absolute Ez over the exported frame set",
            "ClaimBoundary": "internal research visualization only; not external validation, not benchmark evidence, not measurement evidence and not production evidence",
            "AllowedUse": "public website presentation and provenance review",
            "ForbiddenUse": "external validation, measurement evidence, benchmark evidence, production evidence or commercial solver equivalence",
            "InternalResearchOnlyQ": True,
            "ExternalValidationQ": False,
            "ProductionAllowedQ": False,
            "BenchmarkExecutionQ": False,
            "MeasurementDataImportedQ": False,
            "ExternalDataImportedQ": False,
            "PlaceholderImageQ": False,
            "AiGeneratedImageQ": False,
            "InternalPngWriterUsedQ": True,
            "ThirdPartyImageToolUsedQ": False,
            "ExternalPlottingToolUsedQ": False,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        frame_entries.append(
            {
                "FrameIndex": index,
                "ImagePath": relative(frame_path),
                "MetadataPath": relative(metadata_path),
                "TimeStepOrSampleIndex": step,
            }
        )

    manifest = {
        "Title": "FDTD microwave resonator ringdown PNG frame sequence",
        "AssetType": "primary PNG frame sequence",
        "FrameCount": frame_count,
        "FrameDimensionsPx": {"width": SOURCE_FRAME_SIZE[0], "height": SOURCE_FRAME_SIZE[1]},
        "SourceGridSize": {"Nx": SOURCE_GRID_SIZE[0], "Ny": SOURCE_GRID_SIZE[1]},
        "SourceSolver": "DAD FieldWorks 2D TMz FDTD kernel",
        "SourceFieldQuantity": "signed Ez field",
        "RingdownCase": "bounded PEC wall microwave resonator style diagnostic",
        "PecObjectPresentQ": True,
        "InternalPngWriterUsedQ": True,
        "PrimaryEvidenceArtifact": "PNGFrameSequence",
        "DerivedWebsitePreviewFromPngFramesQ": True,
        "GifIsEvidenceArtifactQ": False,
        "ExternalImagesUsedQ": False,
        "ScreenshotsUsedQ": False,
        "GenerativeImageToolsUsedQ": False,
        "PrivateSourceCodeCopiedQ": False,
        "ExternalValidationQ": False,
        "ProductionAllowedQ": False,
        "ClaimBoundary": "internal research visualization only; not external validation, not benchmark evidence, not measurement evidence and not production evidence",
        "Frames": frame_entries,
        "CopyrightHolder": "Harun Aktas",
        "CopyrightNotice": "Copyright (c) 2026 Harun Aktas. All rights reserved.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    README_PATH.write_text(
        "\n".join(
            [
                "# FDTD Ringdown PNG Sequence",
                "",
                "This folder contains the sanitized public PNG frame sequence used as the primary image artifact for the DAD FieldWorks homepage ringdown visual.",
                "",
                "The frames were written with the DAD internal PNG writer from numeric field matrices computed by the DAD FieldWorks 2D TMz FDTD kernel. The derived GIF in `assets/hero/` is a website preview only.",
                "",
                "Claim boundary: internal research visualization only. It is not external validation, not benchmark evidence, not measurement evidence and not production evidence.",
                "",
                "Copyright (c) 2026 Harun Aktas. All rights reserved.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_summary(frames: list[Image.Image]) -> None:
    source_frame_paths = sorted(FRAME_DIR.glob("frame_*.png"))
    summary = {
        "title": "FDTD Microwave Resonator Ringdown Clean Hero",
        "asset_type": "derived public website hero GIF",
        "created_by_script": "scripts/package_fdtd_ringdown_png_sequence_to_gif.py",
        "source_png_sequence": "assets/animations/fdtd_ringdown_png_sequence/frames/",
        "source_frame_count": len(source_frame_paths),
        "gif_frame_count": len(frames),
        "fps": FPS,
        "duration_seconds": round(len(frames) / FPS, 6),
        "dimensions_px": {"width": GIF_SIZE[0], "height": GIF_SIZE[1]},
        "file_size_bytes": GIF_PATH.stat().st_size,
        "derived_from_internal_png_writer_frames": True,
        "DerivedWebsitePreviewFromPngFramesQ": True,
        "primary_evidence_artifact": "PNGFrameSequence",
        "PrimaryEvidenceArtifact": "PNGFrameSequence",
        "gif_is_evidence_artifact": False,
        "GifIsEvidenceArtifactQ": False,
        "text_inside_frames": False,
        "external_images_used": False,
        "screenshots_used": False,
        "generative_image_tools_used": False,
        "private_source_code_copied": False,
        "ProductionAllowedQ": False,
        "ExternalValidationQ": False,
        "external_validation_claim": False,
        "production_claim": False,
        "commercial_solver_equivalence_claim": False,
        "validated_solver_claim": False,
        "claim_boundary": "derived public website preview only; not external validation, not benchmark evidence, not measurement evidence and not production evidence",
        "copyright_holder": "Harun Aktas",
        "copyright_notice": "Copyright (c) 2026 Harun Aktas. All rights reserved.",
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    HERO_DIR.mkdir(parents=True, exist_ok=True)
    frames = load_frames()
    save_optimized_gif(frames)
    frames[len(frames) // 2].save(POSTER_PATH, "PNG", optimize=True)
    write_sequence_metadata(len(frames))
    write_summary(frames)
    print(f"wrote {relative(GIF_PATH)}")
    print(f"wrote {relative(POSTER_PATH)}")
    print(f"wrote {relative(SUMMARY_PATH)}")
    print(f"wrote {relative(MANIFEST_PATH)}")


if __name__ == "__main__":
    main()
