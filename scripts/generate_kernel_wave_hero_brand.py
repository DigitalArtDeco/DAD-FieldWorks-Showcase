"""Deterministic public hero renderer for the DAD FieldWorks website."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "assets" / "brand"
HERO_DIR = ROOT / "assets" / "hero"

A_METERS = 0.080
B_METERS = 0.084
D_METERS = 0.084
MODE = (1, 1, 1)
FIELD_GRID = (960, 450)

HERO_SIZE = (1920, 900)
MARK_SIZE = (1024, 1024)

HERO_PNG = HERO_DIR / "dad_fieldworks_kernel_wave_hero.png"
HERO_WEBP = HERO_DIR / "dad_fieldworks_kernel_wave_hero.webp"
MARK_PNG = BRAND_DIR / "dad_fieldworks_kernel_wave_mark.png"
MARK_POSTER = BRAND_DIR / "dad_fieldworks_kernel_wave_mark_poster.png"
MARK_SVG = BRAND_DIR / "dad_fieldworks_kernel_wave_mark.svg"
SUMMARY_JSON = HERO_DIR / "dad_fieldworks_kernel_wave_hero_summary.json"


def ensure_dirs() -> None:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    HERO_DIR.mkdir(parents=True, exist_ok=True)


def make_field_image(size: tuple[int, int]) -> Image.Image:
    width, height = size
    img = Image.new("RGBA", size)
    px = img.load()
    cx = (width - 1) * 0.5
    cz = (height - 1) * 0.5
    max_r = math.hypot(cx, cz)

    for y in range(height):
        z = y / max(1, height - 1)
        for x in range(width):
            fx = x / max(1, width - 1)
            value = math.sin(math.pi * fx) * math.sin(math.pi * z)
            value = max(0.0, min(1.0, value))
            halo = max(0.0, 1.0 - math.hypot(x - cx, y - cz) / max_r)
            pulse = value ** 0.82
            r = int(8 + 16 * halo + 28 * pulse)
            g = int(22 + 50 * halo + 178 * pulse)
            b = int(38 + 70 * halo + 206 * pulse)
            alpha = int(56 + 176 * pulse)
            px[x, y] = (r, g, b, alpha)

    return img.filter(ImageFilter.GaussianBlur(0.45))


def contour_layer(size: tuple[int, int], color: tuple[int, int, int, int]) -> Image.Image:
    width, height = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    levels = (0.18, 0.32, 0.48, 0.64, 0.78)

    for level in levels:
        top_points: list[tuple[float, float]] = []
        bottom_points: list[tuple[float, float]] = []
        for x in range(1, width - 1, 3):
            sx = math.sin(math.pi * x / max(1, width - 1))
            if sx <= level:
                continue
            z = math.asin(level / sx) / math.pi
            top_points.append((x, z * (height - 1)))
            bottom_points.append((x, (1.0 - z) * (height - 1)))

        if len(top_points) > 2:
            draw.line(top_points, fill=color, width=2, joint="curve")
        if len(bottom_points) > 2:
            draw.line(bottom_points, fill=color, width=2, joint="curve")

    for xfrac in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = int(xfrac * (width - 1))
        draw.line((x, 0, x, height), fill=(70, 112, 145, 34), width=1)
    for zfrac in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = int(zfrac * (height - 1))
        draw.line((0, y, width, y), fill=(70, 112, 145, 34), width=1)

    return layer.filter(ImageFilter.GaussianBlur(0.2))


def draw_y_grid(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], alpha: int) -> None:
    left, top, right, bottom = box
    cols = 24
    rows = 12
    for row in range(rows + 1):
        y = top + (bottom - top) * row / rows
        for col in range(cols + 1):
            x = left + (right - left) * col / cols
            if row in (0, rows) or col in (0, cols):
                radius = 2.2
                color = (244, 167, 82, alpha + 32)
            else:
                radius = 1.45
                color = (120, 166, 196, alpha)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_evidence_nodes(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    nodes = [
        (right + 58, top + 96, (72, 196, 232, 220)),
        (right + 116, top + 238, (242, 139, 47, 220)),
        (right + 76, bottom - 184, (72, 196, 232, 200)),
        (right + 145, bottom - 76, (242, 139, 47, 210)),
    ]
    anchors = [
        (right - 130, top + 120),
        (right - 250, top + 262),
        (right - 190, bottom - 170),
        (right - 90, bottom - 94),
    ]

    for anchor, node in zip(anchors, nodes):
        nx, ny, color = node
        draw.line((anchor[0], anchor[1], nx, ny), fill=(115, 162, 190, 90), width=2)
        draw.rounded_rectangle((nx - 24, ny - 12, nx + 24, ny + 12), radius=7, outline=color, width=2)
        draw.ellipse((anchor[0] - 4, anchor[1] - 4, anchor[0] + 4, anchor[1] + 4), fill=color)


def background(size: tuple[int, int]) -> Image.Image:
    width, height = size
    img = Image.new("RGBA", size)
    px = img.load()
    for y in range(height):
        v = y / max(1, height - 1)
        for x in range(width):
            u = x / max(1, width - 1)
            glow_a = max(0.0, 1.0 - math.hypot(u - 0.18, v - 0.16) / 0.58)
            glow_b = max(0.0, 1.0 - math.hypot(u - 0.80, v - 0.32) / 0.64)
            r = int(3 + 8 * (1 - v) + 10 * glow_b)
            g = int(8 + 15 * (1 - v) + 38 * glow_a + 18 * glow_b)
            b = int(15 + 20 * (1 - v) + 52 * glow_a + 48 * glow_b)
            px[x, y] = (r, g, b, 255)
    return img


def make_hero() -> Image.Image:
    canvas = background(HERO_SIZE)
    draw = ImageDraw.Draw(canvas, "RGBA")

    field_box = (152, 98, 1506, 774)
    panel = make_field_image((FIELD_GRID[0], FIELD_GRID[1]))
    panel = panel.resize((field_box[2] - field_box[0], field_box[3] - field_box[1]), Image.Resampling.BICUBIC)
    contours = contour_layer(panel.size, (194, 245, 255, 152))

    shadow = Image.new("RGBA", HERO_SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    shadow_draw.rounded_rectangle((field_box[0] - 16, field_box[1] - 16, field_box[2] + 18, field_box[3] + 18), radius=44, fill=(0, 0, 0, 132))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    canvas.alpha_composite(shadow)

    draw.rounded_rectangle((field_box[0] - 18, field_box[1] - 18, field_box[2] + 18, field_box[3] + 18), radius=34, fill=(8, 18, 30, 228), outline=(91, 153, 188, 120), width=2)
    canvas.alpha_composite(panel, (field_box[0], field_box[1]))
    canvas.alpha_composite(contours, (field_box[0], field_box[1]))

    draw.rounded_rectangle(field_box, radius=22, outline=(212, 238, 246, 170), width=3)
    draw.rectangle((field_box[0], field_box[1], field_box[2], field_box[1] + 5), fill=(242, 139, 47, 190))
    draw.rectangle((field_box[0], field_box[3] - 5, field_box[2], field_box[3]), fill=(242, 139, 47, 160))
    draw_y_grid(draw, field_box, 58)
    draw_evidence_nodes(draw, field_box)

    for radius, alpha in ((420, 22), (310, 32), (204, 44)):
        draw.ellipse((1050 - radius, 436 - radius, 1050 + radius, 436 + radius), outline=(72, 196, 232, alpha), width=2)

    return canvas.convert("RGB")


def make_mark() -> Image.Image:
    canvas = background(MARK_SIZE)
    draw = ImageDraw.Draw(canvas, "RGBA")
    field_box = (128, 178, 896, 846)
    panel = make_field_image((720, 620)).resize((field_box[2] - field_box[0], field_box[3] - field_box[1]), Image.Resampling.BICUBIC)
    contours = contour_layer(panel.size, (202, 248, 255, 164))

    draw.rounded_rectangle((82, 82, 942, 942), radius=108, fill=(7, 17, 28, 212), outline=(72, 196, 232, 120), width=3)
    canvas.alpha_composite(panel, (field_box[0], field_box[1]))
    canvas.alpha_composite(contours, (field_box[0], field_box[1]))
    draw.rounded_rectangle(field_box, radius=46, outline=(222, 242, 248, 174), width=4)
    draw_y_grid(draw, field_box, 54)
    draw.arc((128, 126, 896, 894), 208, 332, fill=(242, 139, 47, 210), width=8)
    draw.arc((118, 116, 906, 904), 26, 151, fill=(72, 196, 232, 170), width=6)
    for xy, color in [
        ((708, 238), (72, 196, 232, 230)),
        ((800, 468), (242, 139, 47, 230)),
        ((660, 732), (72, 196, 232, 200)),
    ]:
        x, y = xy
        draw.rounded_rectangle((x - 32, y - 15, x + 32, y + 15), radius=9, outline=color, width=3)
    return canvas.convert("RGB")


def write_svg() -> None:
    def contour_path(level: float, upper: bool) -> str:
        commands: list[str] = []
        for i in range(1, 180):
            t = i / 180
            sx = math.sin(math.pi * t)
            if sx <= level:
                continue
            z = math.asin(level / sx) / math.pi
            if not upper:
                z = 1.0 - z
            x = 128 + t * 768
            y = 178 + z * 668
            commands.append(f"{x:.1f},{y:.1f}")
        if len(commands) < 2:
            return ""
        return "M " + " L ".join(commands)

    paths = []
    for level in (0.22, 0.38, 0.56, 0.72):
        for upper in (True, False):
            path = contour_path(level, upper)
            if path:
                paths.append(f'<path d="{path}" fill="none" stroke="#c8f7ff" stroke-width="4" stroke-opacity="0.72"/>')

    svg = "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" role="img" aria-label="DAD FieldWorks kernel wave mark">',
        '<rect width="1024" height="1024" rx="108" fill="#061018"/>',
        '<rect x="128" y="178" width="768" height="668" rx="48" fill="#0b1c2b" stroke="#72c4e8" stroke-opacity="0.72" stroke-width="5"/>',
        *paths,
        '<path d="M 130 846 A 390 390 0 0 0 894 846" fill="none" stroke="#f28b2f" stroke-width="10" stroke-opacity="0.78"/>',
        '<path d="M 130 178 A 390 390 0 0 1 894 178" fill="none" stroke="#48c4e8" stroke-width="8" stroke-opacity="0.68"/>',
        '<circle cx="512" cy="512" r="5" fill="#f3f7fb" fill-opacity="0.92"/>',
        '<rect x="686" y="232" width="64" height="30" rx="9" fill="none" stroke="#48c4e8" stroke-width="4"/>',
        '<rect x="768" y="452" width="64" height="30" rx="9" fill="none" stroke="#f28b2f" stroke-width="4"/>',
        '<rect x="628" y="718" width="64" height="30" rx="9" fill="none" stroke="#48c4e8" stroke-width="4"/>',
        '</svg>',
        '',
    ])
    MARK_SVG.write_text(svg, encoding="utf-8")


def save_assets() -> list[str]:
    ensure_dirs()
    hero = make_hero()
    mark = make_mark()

    hero.save(HERO_PNG, "PNG", optimize=True)
    mark.save(MARK_PNG, "PNG", optimize=True)
    mark.save(MARK_POSTER, "PNG", optimize=True)
    write_svg()

    outputs = [
        "assets/brand/dad_fieldworks_kernel_wave_mark.png",
        "assets/brand/dad_fieldworks_kernel_wave_mark.svg",
        "assets/brand/dad_fieldworks_kernel_wave_mark_poster.png",
        "assets/hero/dad_fieldworks_kernel_wave_hero.png",
    ]

    try:
        hero.save(HERO_WEBP, "WEBP", quality=92, method=6)
        outputs.append("assets/hero/dad_fieldworks_kernel_wave_hero.webp")
    except OSError:
        pass

    summary = {
        "title": "DAD FieldWorks Kernel Wave Hero",
        "asset_type": "deterministic public website hero graphic",
        "created_by_script": "scripts/generate_kernel_wave_hero_brand.py",
        "data_source": "Public safe rectangular PEC cavity mode 111 scalar field specification with a=0.080 m, b=0.084 m, d=0.084 m.",
        "kernel_family": "Rectangular PEC cavity scalar eigenmode reference",
        "field_quantity": "Mode 111 scalar field slice E(x,z)=sin(pi x/a) sin(pi z/d)",
        "grid_size": {"x": FIELD_GRID[0], "z": FIELD_GRID[1]},
        "dimensions_px": {
            "hero": {"width": HERO_SIZE[0], "height": HERO_SIZE[1]},
            "mark": {"width": MARK_SIZE[0], "height": MARK_SIZE[1]},
        },
        "mode_index": {"m": MODE[0], "n": MODE[1], "p": MODE[2]},
        "cavity_dimensions_m": {"a": A_METERS, "b": B_METERS, "d": D_METERS},
        "output_files": outputs + ["assets/hero/dad_fieldworks_kernel_wave_hero_summary.json"],
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
        "claim_boundary": "public brand visualization derived from a scalar reference field; bounded internal diagnostic only.",
        "copyright_holder": "DigitalArtDeco Labs UG (haftungsbeschränkt)",
        "copyright_notice": "Copyright (c) 2026 DigitalArtDeco Labs UG (haftungsbeschränkt). All rights reserved.",
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary["output_files"]


if __name__ == "__main__":
    for output in save_assets():
        print(output)
