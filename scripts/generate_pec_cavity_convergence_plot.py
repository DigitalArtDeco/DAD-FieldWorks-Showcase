from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1280
HEIGHT = 720
FPS = 10
FRAMES = 120
DURATION_SECONDS = FRAMES / FPS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "animations" / "pec_cavity_convergence"
TEMP_DIR = ROOT / ".local_temp" / "pec_cavity_convergence_generation"

GIF_PATH = OUTPUT_DIR / "pec_cavity_convergence_plot.gif"
POSTER_PATH = OUTPUT_DIR / "pec_cavity_convergence_plot_poster.png"
SUMMARY_PATH = OUTPUT_DIR / "pec_cavity_convergence_summary.json"

A = 0.080
B = 0.084
D = 0.084
C0 = 299_792_458.0
MODE = [1, 1, 1]
GRID_LEVELS = [8, 12, 16, 20]

BG = (4, 8, 14)
PANEL = (12, 22, 34)
PANEL_2 = (16, 30, 45)
TEXT = (235, 242, 247)
MUTED = (166, 181, 194)
LINE = (45, 66, 86)
CYAN = (38, 181, 223)
ORANGE = (242, 139, 47)
WARM = (234, 82, 75)
COOL = (64, 151, 236)
GREENISH = (116, 210, 168)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        ["DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"]
        if bold
        else ["DejaVuSans.ttf", "Arial.ttf", "arial.ttf"]
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


FONTS = {
    "title": font(34, True),
    "subtitle": font(20),
    "h2": font(24, True),
    "h3": font(18, True),
    "body": font(16),
    "small": font(13),
    "tiny": font(11),
    "metric": font(21, True),
}


def analytical_frequency_hz() -> float:
    return C0 / 2.0 * math.sqrt((1 / A) ** 2 + (1 / B) ** 2 + (1 / D) ** 2)


def discrete_frequency_hz(n: int) -> float:
    hx = A / (n + 1)
    hy = B / (n + 1)
    hz = D / (n + 1)
    lambda_h = (
        4 / hx**2 * math.sin(math.pi / (2 * (n + 1))) ** 2
        + 4 / hy**2 * math.sin(math.pi / (2 * (n + 1))) ** 2
        + 4 / hz**2 * math.sin(math.pi / (2 * (n + 1))) ** 2
    )
    return C0 / (2 * math.pi) * math.sqrt(lambda_h)


def convergence_rows() -> list[dict[str, float | int]]:
    f_ref = analytical_frequency_hz()
    rows = []
    for n in GRID_LEVELS:
        f_h = discrete_frequency_hz(n)
        rel = abs(f_h - f_ref) / f_ref
        rows.append(
            {
                "grid": n,
                "frequency_hz": f_h,
                "frequency_ghz": f_h / 1.0e9,
                "relative_error": rel,
                "relative_error_percent": 100.0 * rel,
            }
        )
    return rows


def rounded_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill, outline=LINE, width=1, radius=16):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_text(draw: ImageDraw.ImageDraw, xy, text, fill=TEXT, font_name="body", anchor=None, align="left"):
    draw.text(xy, text, fill=fill, font=FONTS[font_name], anchor=anchor, align=align)


def amp_color(value: float) -> tuple[int, int, int]:
    v = max(-1.0, min(1.0, value))
    if v >= 0:
        t = v
        base = (28, 34, 44)
        return tuple(int(base[i] * (1 - t) + WARM[i] * t) for i in range(3))
    t = -v
    base = (28, 34, 44)
    return tuple(int(base[i] * (1 - t) + COOL[i] * t) for i in range(3))


def field_slice_image(phase: float, px_w: int = 350, px_h: int = 210) -> Image.Image:
    small_w, small_h = 90, 54
    img = Image.new("RGB", (small_w, small_h), (22, 28, 36))
    pix = img.load()
    phase_factor = math.cos(phase)
    for j in range(small_h):
        y = (j + 0.5) / small_h
        for i in range(small_w):
            x = (i + 0.5) / small_w
            amp = math.sin(math.pi * x) * math.sin(math.pi * y) * phase_factor
            pix[i, j] = amp_color(amp)
    return img.resize((px_w, px_h), Image.Resampling.BICUBIC)


def draw_cavity_panel(draw: ImageDraw.ImageDraw, frame: Image.Image, active_grid: int, phase: float):
    panel = (48, 126, 555, 592)
    rounded_rect(draw, panel, PANEL)
    draw_text(draw, (76, 150), "Rectangular PEC cavity", CYAN, "h2")
    draw_text(draw, (76, 181), "80 mm x 84 mm x 84 mm  |  mode 111 scalar reference", MUTED, "small")

    front = (110, 274, 460, 484)
    dx, dy = 58, -48
    back = tuple([front[0] + dx, front[1] + dy, front[2] + dx, front[3] + dy])

    draw.rectangle(back, outline=(62, 82, 104), width=2)
    for x0, y0, x1, y1 in [
        (front[0], front[1], back[0], back[1]),
        (front[2], front[1], back[2], back[1]),
        (front[0], front[3], back[0], back[3]),
        (front[2], front[3], back[2], back[3]),
    ]:
        draw.line((x0, y0, x1, y1), fill=(62, 82, 104), width=2)

    slice_img = field_slice_image(phase, front[2] - front[0], front[3] - front[1])
    frame.paste(slice_img, (front[0], front[1]))

    grid_lines = max(4, min(active_grid, 20))
    for k in range(grid_lines + 1):
        x = front[0] + (front[2] - front[0]) * k / grid_lines
        y = front[1] + (front[3] - front[1]) * k / grid_lines
        draw.line((x, front[1], x, front[3]), fill=(255, 255, 255, 48), width=1)
        draw.line((front[0], y, front[2], y), fill=(255, 255, 255, 48), width=1)
    draw.rectangle(front, outline=(120, 140, 160), width=2)

    draw_text(draw, (76, 522), f"Active grid: {active_grid}^3", TEXT, "metric")
    draw_text(draw, (76, 554), "warm/cool scalar standing-mode phase impression", MUTED, "small")


def active_index(progress: float) -> int:
    if progress < 0.18:
        return 0
    if progress < 0.38:
        return 1
    if progress < 0.58:
        return 2
    return 3


def draw_reference_header(draw: ImageDraw.ImageDraw, f_ref: float):
    draw_text(draw, (640, 34), "PEC Cavity Convergence Plot", TEXT, "title", anchor="ma")
    draw_text(
        draw,
        (640, 72),
        "Grid refinement against an analytical rectangular PEC cavity reference",
        MUTED,
        "subtitle",
        anchor="ma",
    )
    rounded_rect(draw, (430, 92, 850, 122), (9, 16, 25), outline=(38, 84, 108), radius=10)
    draw_text(
        draw,
        (640, 107),
        f"Analytical reference: f_111 = {f_ref / 1.0e9:.9f} GHz",
        CYAN,
        "h3",
        anchor="mm",
    )


def draw_plot_panel(draw: ImageDraw.ImageDraw, rows: list[dict[str, float | int]], active: int):
    panel = (585, 126, 1232, 592)
    rounded_rect(draw, panel, PANEL)
    draw_text(draw, (615, 150), "Computed convergence trend", CYAN, "h2")
    draw_text(draw, (615, 181), "relative error from discrete scalar diagnostic", MUTED, "small")

    card = (615, 204, 1202, 292)
    rounded_rect(draw, card, PANEL_2, outline=(50, 74, 96), radius=12)
    row = rows[active]
    draw_text(draw, (636, 226), f"Grid: {int(row['grid'])}^3", TEXT, "metric")
    draw_text(draw, (636, 255), f"Numerical f: {row['frequency_ghz']:.9f} GHz", TEXT, "h3")
    draw_text(draw, (925, 255), f"Relative error: {row['relative_error_percent']:.4f} %", ORANGE, "h3")

    x0, y0, x1, y1 = 650, 350, 1165, 540
    draw.line((x0, y1, x1, y1), fill=MUTED, width=2)
    draw.line((x0, y0, x0, y1), fill=MUTED, width=2)
    draw_text(draw, ((x0 + x1) // 2, 570), "grid resolution", MUTED, "small", anchor="ma")
    draw_text(draw, (604, 445), "relative error (%)", MUTED, "small")

    max_err = max(float(r["relative_error_percent"]) for r in rows) * 1.12
    min_err = 0.0
    x_positions = []
    for i, r in enumerate(rows):
        x = x0 + (x1 - x0) * i / (len(rows) - 1)
        x_positions.append(x)
        draw.line((x, y1 - 4, x, y1 + 4), fill=MUTED, width=1)
        draw_text(draw, (x, y1 + 13), f"{int(r['grid'])}^3", MUTED, "tiny", anchor="ma")

    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = y1 - (y1 - y0) * frac
        val = min_err + (max_err - min_err) * frac
        draw.line((x0, y, x1, y), fill=(32, 49, 65), width=1)
        draw_text(draw, (x0 - 9, y), f"{val:.2f}", MUTED, "tiny", anchor="rm")

    points = []
    for i in range(active + 1):
        err = float(rows[i]["relative_error_percent"])
        y = y1 - (err - min_err) / (max_err - min_err) * (y1 - y0)
        points.append((x_positions[i], y))

    if len(points) > 1:
        draw.line(points, fill=CYAN, width=4)
    for i, point in enumerate(points):
        draw.ellipse((point[0] - 7, point[1] - 7, point[0] + 7, point[1] + 7), fill=ORANGE, outline=TEXT, width=2)
        draw_text(draw, (point[0], point[1] - 24), f"{rows[i]['relative_error_percent']:.3f}%", TEXT, "tiny", anchor="ma")

    if active == len(rows) - 1:
        note = (790, 304, 1202, 336)
        rounded_rect(draw, note, (12, 30, 31), outline=(58, 110, 95), radius=10)
        draw_text(draw, (996, 320), "computed - compared - bounded", GREENISH, "h3", anchor="mm")


def draw_footer(draw: ImageDraw.ImageDraw):
    rounded_rect(draw, (48, 626, 1232, 678), (8, 14, 22), outline=(42, 64, 84), radius=14)
    draw_text(
        draw,
        (640, 652),
        "bounded scalar PEC diagnostic - analytical reference comparison, no external validation or production claim",
        MUTED,
        "h3",
        anchor="mm",
    )


def draw_interpretation(draw: ImageDraw.ImageDraw, progress: float):
    if progress < 0.78:
        return
    box = (76, 204, 425, 256)
    rounded_rect(draw, box, (10, 22, 30), outline=(38, 84, 108), radius=12)
    draw_text(draw, (96, 220), "Evidence status", CYAN, "h3")
    draw_text(draw, (96, 242), "computed sequence | bounded diagnostic", TEXT, "small")


def render_frame(frame_index: int, rows: list[dict[str, float | int]], f_ref: float) -> Image.Image:
    progress = frame_index / (FRAMES - 1)
    phase = 2 * math.pi * (1.0 + 1.3 * progress)
    active = active_index(progress)
    active_grid = int(rows[active]["grid"])

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_reference_header(draw, f_ref)
    draw_cavity_panel(draw, img, active_grid, phase)
    draw_plot_panel(draw, rows, active)
    draw_interpretation(draw, progress)
    draw_footer(draw)
    return img


def write_summary(rows: list[dict[str, float | int]], f_ref: float):
    errors = [float(r["relative_error"]) for r in rows]
    summary = {
        "title": "PEC Cavity Convergence Plot",
        "subtitle": "Grid refinement against an analytical rectangular PEC cavity reference",
        "created_by_script": "scripts/generate_pec_cavity_convergence_plot.py",
        "model_type": "deterministic scalar finite-difference PEC cavity diagnostic",
        "data_source": "closed-form analytical reference and exact discrete scalar Helmholtz finite-difference formula",
        "fallback_used": True,
        "cavity_dimensions_m": {"a": A, "b": B, "d": D},
        "mode": MODE,
        "analytical_frequency_hz": f_ref,
        "analytical_frequency_ghz": f_ref / 1.0e9,
        "grid_levels": [int(r["grid"]) for r in rows],
        "numerical_frequencies_hz": [float(r["frequency_hz"]) for r in rows],
        "numerical_frequencies_ghz": [float(r["frequency_ghz"]) for r in rows],
        "relative_errors": errors,
        "relative_errors_percent": [float(r["relative_error_percent"]) for r in rows],
        "final_grid": int(rows[-1]["grid"]),
        "final_relative_error": errors[-1],
        "convergence_trend": "relative error decreases monotonically with grid refinement",
        "frames": FRAMES,
        "duration_seconds": DURATION_SECONDS,
        "ProductionAllowedQ": False,
        "ExternalValidationQ": False,
        "external_validation_claim": False,
        "production_claim": False,
        "commercial_solver_equivalence_claim": False,
        "validated_eigenmode_claim": False,
        "qubit_simulation_claim": False,
        "quantum_device_claim": False,
        "cpml_claim": False,
        "arbitrary_geometry_claim": False,
        "external_images_used": False,
        "screenshots_used": False,
        "generative_image_tools_used": False,
        "private_source_code_copied": False,
        "claim_boundary": "bounded scalar PEC diagnostic only; analytical reference comparison, not external validation and not production readiness",
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    f_ref = analytical_frequency_hz()
    rows = convergence_rows()
    if not all(rows[i]["relative_error"] > rows[i + 1]["relative_error"] for i in range(len(rows) - 1)):
        raise RuntimeError("Relative error must decrease with grid refinement.")

    frames = [render_frame(i, rows, f_ref) for i in range(FRAMES)]
    frames[-1].save(POSTER_PATH)
    frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True,
        disposal=2,
    )
    write_summary(rows, f_ref)

    print(f"Wrote {GIF_PATH.relative_to(ROOT)}")
    print(f"Wrote {POSTER_PATH.relative_to(ROOT)}")
    print(f"Wrote {SUMMARY_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
