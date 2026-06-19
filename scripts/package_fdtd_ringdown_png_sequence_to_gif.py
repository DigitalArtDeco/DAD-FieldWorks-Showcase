"""Package the public FDTD ringdown PNG sequence as a website GIF preview.

This script intentionally does not compute field data. It reads the sanitized
public PNG frames, resizes them for the website hero, applies GIF palette
optimization, and writes the derived GIF, poster frame, and summary JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
FRAME_DIR = REPO_ROOT / "assets" / "animations" / "fdtd_ringdown_png_sequence" / "frames"
HERO_DIR = REPO_ROOT / "assets" / "hero"
GIF_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero.gif"
POSTER_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero_poster.png"
SUMMARY_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero_summary.json"
SCRIPT_PATH = "scripts/package_fdtd_ringdown_png_sequence_to_gif.py"

TARGET_SIZE = (640, 360)
FPS = 12
TARGET_BYTES = 4 * 1024 * 1024
HARD_MAX_BYTES = 5 * 1024 * 1024


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def load_frames() -> list[Image.Image]:
    frame_paths = sorted(FRAME_DIR.glob("frame_*.png"))
    if len(frame_paths) < 48:
        raise RuntimeError(f"Expected at least 48 sanitized PNG frames, found {len(frame_paths)}.")

    frames: list[Image.Image] = []
    for frame_path in frame_paths:
        with Image.open(frame_path) as image:
            frame = image.convert("RGB")
            if frame.size != TARGET_SIZE:
                frame = frame.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
            frames.append(frame)
    return frames


def quantize_frames(frames: list[Image.Image], colors: int) -> list[Image.Image]:
    return [
        frame.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        for frame in frames
    ]


def write_gif(frames: list[Image.Image], colors: int) -> int:
    quantized = quantize_frames(frames, colors)
    duration_ms = round(1000 / FPS)
    quantized[0].save(
        GIF_PATH,
        save_all=True,
        append_images=quantized[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return GIF_PATH.stat().st_size


def write_summary(frame_count: int, file_size: int) -> None:
    summary = {
        "title": "FDTD microwave resonator ringdown clean hero",
        "asset_type": "derived website GIF preview from sanitized PNG frames",
        "created_by_script": SCRIPT_PATH,
        "source_png_sequence": "assets/animations/fdtd_ringdown_png_sequence/frames/",
        "source_frame_count": frame_count,
        "gif_frame_count": frame_count,
        "fps": FPS,
        "duration_seconds": round(frame_count / FPS, 3),
        "dimensions_px": {"width": TARGET_SIZE[0], "height": TARGET_SIZE[1]},
        "file_size_bytes": file_size,
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
        "claim_boundary": (
            "Derived public website preview from DAD PNG writer frames generated "
            "from internal FDTD microwave resonator ringdown solver output. Not "
            "external validation, not measurement evidence, not benchmark evidence "
            "and not production evidence."
        ),
        "copyright_holder": "Harun Aktas",
        "copyright_notice": "Copyright © 2026 Harun Aktas. All rights reserved.",
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    HERO_DIR.mkdir(parents=True, exist_ok=True)
    frames = load_frames()
    frames[0].save(POSTER_PATH)

    selected_size = 0
    for colors in (128, 96, 80, 64, 48):
        selected_size = write_gif(frames, colors)
        if selected_size <= TARGET_BYTES:
            break

    if selected_size > HARD_MAX_BYTES:
        raise RuntimeError(
            f"Generated GIF is {selected_size} bytes, above hard maximum {HARD_MAX_BYTES} bytes."
        )

    write_summary(len(frames), selected_size)
    print(f"Wrote {repo_relative(GIF_PATH)} ({selected_size} bytes)")
    print(f"Wrote {repo_relative(POSTER_PATH)}")
    print(f"Wrote {repo_relative(SUMMARY_PATH)}")


if __name__ == "__main__":
    main()
