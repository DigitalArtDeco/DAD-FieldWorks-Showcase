from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "animations" / "pcb2d_microstrip_field_scientific_v2_sequence"
FRAME_DIR = SOURCE_DIR / "frames"
HERO_DIR = ROOT / "assets" / "hero"
GIF_PATH = HERO_DIR / "pcb2d_microstrip_field_scientific_v2_hero.gif"
POSTER_PATH = HERO_DIR / "pcb2d_microstrip_field_scientific_v2_hero_poster.png"
SUMMARY_PATH = HERO_DIR / "pcb2d_microstrip_field_scientific_v2_hero_summary.json"


def selected_frames(frame_paths: list[Path], count: int) -> list[Path]:
    if count >= len(frame_paths):
        return frame_paths
    if count <= 1:
        return [frame_paths[0]]
    return [
        frame_paths[round(i * (len(frame_paths) - 1) / (count - 1))]
        for i in range(count)
    ]


def load_frames(paths: list[Path], size: tuple[int, int]) -> list[Image.Image]:
    frames: list[Image.Image] = []
    for path in paths:
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            if rgb.size != size:
                rgb = rgb.resize(size, Image.Resampling.LANCZOS)
            frames.append(rgb.convert("P", palette=Image.Palette.ADAPTIVE, colors=192))
    return frames


def write_gif(paths: list[Path], size: tuple[int, int], fps: int) -> int:
    HERO_DIR.mkdir(parents=True, exist_ok=True)
    frames = load_frames(paths, size)
    duration_ms = round(1000 / fps)
    frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return GIF_PATH.stat().st_size


def main() -> None:
    frame_paths = sorted(FRAME_DIR.glob("frame_*.png"))
    if len(frame_paths) < 60:
        raise SystemExit("At least 60 source PNG frames are required.")

    candidates = [
        (96, (800, 600), 24),
        (72, (800, 600), 24),
        (72, (640, 480), 24),
        (60, (640, 480), 18),
    ]
    chosen: tuple[int, tuple[int, int], int, int] | None = None
    for frame_count, size, fps in candidates:
        paths = selected_frames(frame_paths, frame_count)
        file_size = write_gif(paths, size, fps)
        chosen = (len(paths), size, fps, file_size)
        if file_size <= 12 * 1024 * 1024:
            break

    if chosen is None:
        raise SystemExit("GIF packaging failed.")

    gif_frame_count, gif_size, fps, file_size = chosen
    if file_size > 12 * 1024 * 1024:
        raise SystemExit("GIF exceeds 12 MB hard maximum.")

    poster_source = frame_paths[len(frame_paths) // 2]
    with Image.open(poster_source) as image:
        image.convert("RGB").save(POSTER_PATH)

    summary = {
        "title": "PCB 2D microstrip scientific field hero",
        "asset_type": "derived website GIF",
        "created_by_script": "scripts/package_pcb2d_microstrip_field_scientific_v2_to_gif.py",
        "source_png_sequence": "assets/animations/pcb2d_microstrip_field_scientific_v2_sequence/frames",
        "source_frame_count": len(frame_paths),
        "gif_frame_count": gif_frame_count,
        "fps": fps,
        "duration_seconds": round(gif_frame_count / fps, 4),
        "source_dimensions_px": [800, 600],
        "gif_dimensions_px": list(gif_size),
        "file_size_bytes": file_size,
        "source_field_quantity": "electric_field_magnitude_v_per_m",
        "color_mapping": "dadfw-blue-red-linear-v2",
        "normalization_method": "fixed global colorbar range across all frames",
        "drive_amplitude_sweep": "0.10 to 1.00 to 0.10 smooth cosine envelope",
        "derived_from_internal_png_writer_frames": True,
        "primary_evidence_artifact": "PNGFrameSequence",
        "gif_is_evidence_artifact": False,
        "external_images_used": False,
        "screenshots_used": False,
        "generative_image_tools_used": False,
        "python_plotting_used": False,
        "private_source_code_copied": False,
        "ProductionAllowedQ": False,
        "ExternalValidationQ": False,
        "external_validation_claim": False,
        "production_claim": False,
        "commercial_solver_equivalence_claim": False,
        "validated_solver_claim": False,
        "claim_boundary": "Website preview only from internal PCB 2D quasi-static field data; no external validation claim and no production readiness claim.",
        "copyright_holder": "DigitalArtDeco Labs UG (haftungsbeschränkt)",
        "copyright_notice": "Copyright 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.",
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {GIF_PATH} ({file_size} bytes, {gif_frame_count} frames at {fps} fps).")


if __name__ == "__main__":
    main()
