"""Create the text-free FDTD microwave resonator ringdown hero animation."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
HERO_DIR = ROOT / "assets" / "hero"

GIF_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero.gif"
POSTER_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero_poster.png"
SUMMARY_PATH = HERO_DIR / "fdtd_microwave_resonator_ringdown_clean_hero_summary.json"

NX = 168
NY = 96
TOTAL_STEPS = 360
FRAME_STRIDE = 4
FPS = 12.5
FRAME_SIZE = (640, 360)
POSTER_SIZE = (1280, 720)

CAVITY_LEFT = 68
CAVITY_RIGHT = 154
CAVITY_TOP = 20
CAVITY_BOTTOM = 78
SLOT_TOP = 43
SLOT_BOTTOM = 54
FEED_TOP = 43
FEED_BOTTOM = 54
POST_LEFT = 124
POST_RIGHT = 132
POST_TOP = 44
POST_BOTTOM = 56


def make_absorber() -> np.ndarray:
    edge = 14
    damp = np.ones((NX, NY), dtype=np.float64)
    for i in range(NX):
        for j in range(NY):
            d = min(i, j, NX - 1 - i, NY - 1 - j)
            if d < edge:
                strength = ((edge - d) / edge) ** 2
                damp[i, j] = 1.0 - 0.060 * strength
    return damp


def make_pec_mask() -> np.ndarray:
    mask = np.zeros((NX, NY), dtype=bool)
    mask[:, 0] = True
    mask[:, NY - 1] = True
    mask[0, :] = True
    mask[NX - 1, :] = True

    mask[: CAVITY_LEFT + 1, FEED_TOP] = True
    mask[: CAVITY_LEFT + 1, FEED_BOTTOM] = True
    mask[CAVITY_LEFT:CAVITY_RIGHT + 1, CAVITY_TOP] = True
    mask[CAVITY_LEFT:CAVITY_RIGHT + 1, CAVITY_BOTTOM] = True
    mask[CAVITY_RIGHT, CAVITY_TOP:CAVITY_BOTTOM + 1] = True
    mask[CAVITY_LEFT, CAVITY_TOP:SLOT_TOP] = True
    mask[CAVITY_LEFT, SLOT_BOTTOM:CAVITY_BOTTOM + 1] = True
    mask[POST_LEFT:POST_RIGHT + 1, POST_TOP:POST_BOTTOM + 1] = True
    return mask


def run_fdtd() -> list[np.ndarray]:
    ez = np.zeros((NX, NY), dtype=np.float64)
    hx = np.zeros((NX, NY - 1), dtype=np.float64)
    hy = np.zeros((NX - 1, NY), dtype=np.float64)
    damp = make_absorber()
    damp_hx = 0.5 * (damp[:, 1:] + damp[:, :-1])
    damp_hy = 0.5 * (damp[1:, :] + damp[:-1, :])
    pec = make_pec_mask()
    frames: list[np.ndarray] = []

    ch = 0.49
    ce = 0.49
    global_loss = 0.9994
    source_x = 13
    source_slice = slice(FEED_TOP + 2, FEED_BOTTOM - 1)

    for step in range(TOTAL_STEPS):
        hx -= ch * (ez[:, 1:] - ez[:, :-1])
        hy += ch * (ez[1:, :] - ez[:-1, :])
        hx *= damp_hx * global_loss
        hy *= damp_hy * global_loss

        curl_h = (hy[1:, 1:-1] - hy[:-1, 1:-1]) - (hx[1:-1, 1:] - hx[1:-1, :-1])
        ez[1:-1, 1:-1] += ce * curl_h

        pulse = math.sin(0.42 * step) * math.exp(-((step - 54.0) / 23.0) ** 2)
        ez[source_x, source_slice] += 1.18 * pulse

        ez *= damp * global_loss
        ez[pec] = 0.0

        if step % FRAME_STRIDE == 0:
            frames.append(ez.copy())

    return frames


def colorize(field: np.ndarray, scale: float) -> Image.Image:
    v = np.tanh(2.15 * field / max(scale, 1.0e-9))
    mag = np.abs(v) ** 0.72
    positive = np.clip(v, 0.0, 1.0)
    negative = np.clip(-v, 0.0, 1.0)

    base = np.zeros((NY, NX, 3), dtype=np.float64)
    base[:, :, 0] = 4
    base[:, :, 1] = 11
    base[:, :, 2] = 20

    arr = base.copy()
    arr[:, :, 0] += 22 * mag.T + 232 * negative.T
    arr[:, :, 1] += 38 * mag.T + 88 * negative.T + 195 * positive.T
    arr[:, :, 2] += 58 * mag.T + 16 * negative.T + 226 * positive.T
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def gradient_background(size: tuple[int, int]) -> Image.Image:
    width, height = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(height):
        yy = y / max(1, height - 1)
        for x in range(width):
            xx = x / max(1, width - 1)
            glow = max(0.0, 1.0 - math.hypot(xx - 0.52, yy - 0.48) / 0.72)
            r = int(3 + 8 * glow)
            g = int(8 + 20 * glow)
            b = int(17 + 34 * glow)
            px[x, y] = (r, g, b)
    return img


def draw_geometry(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    width = right - left
    height = bottom - top

    def sx(i: float) -> float:
        return left + width * i / (NX - 1)

    def sy(j: float) -> float:
        return top + height * j / (NY - 1)

    line = (194, 239, 248)
    muted = (86, 147, 180)
    warm = (242, 139, 47)

    for j in (FEED_TOP, FEED_BOTTOM):
        draw.line((sx(0), sy(j), sx(CAVITY_LEFT), sy(j)), fill=muted, width=2)

    draw.line((sx(CAVITY_LEFT), sy(CAVITY_TOP), sx(CAVITY_RIGHT), sy(CAVITY_TOP)), fill=line, width=2)
    draw.line((sx(CAVITY_LEFT), sy(CAVITY_BOTTOM), sx(CAVITY_RIGHT), sy(CAVITY_BOTTOM)), fill=line, width=2)
    draw.line((sx(CAVITY_RIGHT), sy(CAVITY_TOP), sx(CAVITY_RIGHT), sy(CAVITY_BOTTOM)), fill=line, width=2)
    draw.line((sx(CAVITY_LEFT), sy(CAVITY_TOP), sx(CAVITY_LEFT), sy(SLOT_TOP)), fill=line, width=2)
    draw.line((sx(CAVITY_LEFT), sy(SLOT_BOTTOM), sx(CAVITY_LEFT), sy(CAVITY_BOTTOM)), fill=line, width=2)
    draw.line((sx(CAVITY_LEFT), sy(SLOT_TOP), sx(CAVITY_LEFT), sy(SLOT_BOTTOM)), fill=warm, width=1)
    draw.rounded_rectangle(
        (sx(POST_LEFT), sy(POST_TOP), sx(POST_RIGHT), sy(POST_BOTTOM)),
        radius=4,
        outline=warm,
        width=2,
    )

    for frac in (0.25, 0.5, 0.75):
        x = int(left + frac * width)
        draw.line((x, top, x, bottom), fill=(70, 112, 145), width=1)
    for frac in (0.25, 0.5, 0.75):
        y = int(top + frac * height)
        draw.line((left, y, right, y), fill=(70, 112, 145), width=1)


def render_frame(field: np.ndarray, scale: float, size: tuple[int, int]) -> Image.Image:
    width, height = size
    canvas = gradient_background(size)
    draw = ImageDraw.Draw(canvas)
    margin_x = int(width * 0.055)
    margin_y = int(height * 0.11)
    box = (margin_x, margin_y, width - margin_x, height - margin_y)

    panel = colorize(field, scale).resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.BICUBIC)
    canvas.paste(panel, (box[0], box[1]))
    draw.rounded_rectangle((box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4), radius=14, outline=(62, 192, 224), width=1)
    draw_geometry(draw, box)
    return canvas


def save_gif(frames: list[Image.Image]) -> None:
    duration_ms = int(1000 / FPS)
    palette_frames = [
        frame.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
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


def build_assets() -> dict[str, object]:
    HERO_DIR.mkdir(parents=True, exist_ok=True)
    fields = run_fdtd()
    scale = float(max(np.max(np.abs(field)) for field in fields))
    rendered = [render_frame(field, scale, FRAME_SIZE) for field in fields]
    save_gif(rendered)

    poster_field = fields[int(len(fields) * 0.62)]
    poster = render_frame(poster_field, scale, POSTER_SIZE)
    poster.save(POSTER_PATH, "PNG", optimize=True)

    output_files = [
        "assets/hero/fdtd_microwave_resonator_ringdown_clean_hero.gif",
        "assets/hero/fdtd_microwave_resonator_ringdown_clean_hero_poster.png",
        "assets/hero/fdtd_microwave_resonator_ringdown_clean_hero_summary.json",
    ]

    summary = {
        "title": "FDTD Microwave Resonator Ringdown Clean Hero",
        "asset_type": "text-free deterministic public website hero animation",
        "created_by_script": "scripts/generate_fdtd_microwave_resonator_ringdown_clean_hero.py",
        "data_source": "Deterministic public-safe 2D FDTD TMz diagnostic computation following the existing public resonator ringdown provenance.",
        "kernel_family": "2D FDTD TMz microwave resonator diagnostic",
        "field_quantity": "signed Ez field",
        "geometry_summary": "line-coupled resonator with feed guide, coupling slot, rectangular cavity, central post and graded-loss edge absorber",
        "frames": len(rendered),
        "fps": FPS,
        "duration_seconds": round(len(rendered) / FPS, 3),
        "dimensions_px": {"width": FRAME_SIZE[0], "height": FRAME_SIZE[1]},
        "file_size_bytes": {
            "gif": GIF_PATH.stat().st_size,
            "poster_png": POSTER_PATH.stat().st_size,
        },
        "text_inside_frames": False,
        "output_files": output_files,
        "private_repo_read": False,
        "private_code_executed": False,
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
        "claim_boundary": "deterministic public-safe FDTD microwave resonator ringdown diagnostic only; not external validation, not production readiness and not commercial solver equivalence",
        "copyright_holder": "Harun Aktas",
        "copyright_notice": "Copyright (c) 2026 Harun Aktas. All rights reserved.",
    }
    for _ in range(4):
        SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        current_size = SUMMARY_PATH.stat().st_size
        if summary["file_size_bytes"].get("summary_json") == current_size:
            break
        summary["file_size_bytes"]["summary_json"] = current_size
    return summary


if __name__ == "__main__":
    result = build_assets()
    for output_file in result["output_files"]:
        print(output_file)
