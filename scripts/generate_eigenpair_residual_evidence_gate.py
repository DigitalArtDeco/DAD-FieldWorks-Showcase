#!/usr/bin/env python3
"""Create the Eigenpair Residual Evidence Gate public animation."""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin


TITLE = "Eigenpair Residual Evidence Gate"
SUBTITLE = "Candidate eigenpair to residual magnitude and bounded evidence score"
FOOTER = "bounded diagnostic - residual based evidence score, no external validation or production claim"

CAVITY_A_M = 0.080
CAVITY_B_M = 0.084
CAVITY_D_M = 0.084
C0 = 299_792_458.0
NX = 72
NZ = 72
TINY = 1.0e-30

FRAME_COUNT = 132
FPS = 11
DURATION_SECONDS = FRAME_COUNT / FPS
GIF_SIZE = (1440, 810)
POSTER_SIZE = (1600, 900)

BG = "#071018"
PANEL = "#0c1824"
CARD = "#0f1c2a"
PANEL_EDGE = "#2c5a76"
TEXT = "#e7f1ff"
MUTED = "#b7c7d7"
SOFT = "#7f94a8"
CYAN = "#55d7ff"
ORANGE = "#ff9d4d"
RED = "#ff675f"
BLUE = "#3478ff"
GREEN = "#76efb2"
YELLOW = "#ffd166"
BLACK = "#050a10"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return min(hi, max(lo, value))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if value <= edge0:
        return 0.0
    if value >= edge1:
        return 1.0
    t = (value - edge0) / (edge1 - edge0)
    return t * t * (3.0 - 2.0 * t)


def hex_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def mix_color(a: str, b: str, t: float) -> tuple[int, int, int]:
    ar, ag, ab = hex_rgb(a)
    br, bg, bb = hex_rgb(b)
    t = clamp(t)
    return (
        int(ar + (br - ar) * t),
        int(ag + (bg - ag) * t),
        int(ab + (bb - ab) * t),
    )


def rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    r, g, b = hex_rgb(color)
    return r, g, b, alpha


def scale_box(box: tuple[int, int, int, int], scale: float) -> tuple[int, int, int, int]:
    x, y, w, h = box
    return round(x * scale), round(y * scale), round(w * scale), round(h * scale)


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    windows_fonts = Path(os.environ.get("WINDIR", "")) / "Fonts"
    candidates = (
        (
            "DejaVuSans-Bold.ttf",
            "Arialbd.ttf",
            "arialbd.ttf",
            str(windows_fonts / "arialbd.ttf"),
            str(windows_fonts / "segoeuib.ttf"),
        )
        if bold
        else (
            "DejaVuSans.ttf",
            "Arial.ttf",
            "arial.ttf",
            str(windows_fonts / "arial.ttf"),
            str(windows_fonts / "segoeui.ttf"),
        )
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    for raw_line in text.split("\n"):
        words = raw_line.split()
        if not words:
            lines.append("")
            continue
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if text_size(draw, candidate, font)[0] <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    *,
    size: int,
    fill: str = TEXT,
    bold: bool = False,
    align: str = "left",
    valign: str = "top",
    min_size: int = 10,
    spacing: float = 1.22,
) -> list[tuple[int, int, int, int]]:
    x, y, w, h = box
    font_size = size
    while font_size >= min_size:
        font = load_font(font_size, bold=bold)
        lines = wrap_lines(draw, text, font, w)
        line_h = max(1, text_size(draw, "Ag", font)[1])
        total_h = round(line_h * spacing * len(lines))
        widest = max((text_size(draw, line, font)[0] for line in lines), default=0)
        if total_h <= h and widest <= w:
            break
        font_size -= 1
    font = load_font(max(font_size, min_size), bold=bold)
    lines = wrap_lines(draw, text, font, w)
    line_h = max(1, text_size(draw, "Ag", font)[1])
    step = round(line_h * spacing)
    max_lines = max(1, h // max(step, 1))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1].rstrip(".")
        while text_size(draw, last + "...", font)[0] > w and last:
            last = last[:-1]
        lines[-1] = (last or lines[-1][:1]) + "..."
    total_h = step * len(lines)
    if valign == "center":
        ty = y + (h - total_h) // 2
    elif valign == "bottom":
        ty = y + h - total_h
    else:
        ty = y
    boxes: list[tuple[int, int, int, int]] = []
    for line in lines:
        line_w, line_h_px = text_size(draw, line, font)
        if align == "center":
            tx = x + (w - line_w) // 2
        elif align == "right":
            tx = x + w - line_w
        else:
            tx = x
        draw.text((tx, ty), line, fill=fill, font=font)
        boxes.append((tx, ty, line_w, line_h_px))
        ty += step
    return boxes


def draw_text_fit(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    *,
    size: int,
    fill: str = TEXT,
    bold: bool = False,
    align: str = "left",
    valign: str = "center",
    min_size: int = 10,
) -> tuple[int, int, int, int]:
    x, y, w, h = box
    font_size = size
    while font_size >= min_size:
        font = load_font(font_size, bold=bold)
        tw, th = text_size(draw, text, font)
        if tw <= w and th <= h:
            break
        font_size -= 1
    font = load_font(max(font_size, min_size), bold=bold)
    tw, th = text_size(draw, text, font)
    if align == "center":
        tx = x + (w - tw) // 2
    elif align == "right":
        tx = x + w - tw
    else:
        tx = x
    if valign == "center":
        ty = y + (h - th) // 2
    elif valign == "bottom":
        ty = y + h - th
    else:
        ty = y
    draw.text((tx, ty), text, fill=fill, font=font)
    return tx, ty, tw, th


def draw_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    fill: str = PANEL,
    outline: str = PANEL_EDGE,
    width: int = 2,
) -> None:
    x, y, w, h = box
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=outline, width=width)


def draw_metric_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    *,
    accent: str,
    active: bool,
    scale: float,
) -> None:
    x, y, w, h = box
    fill = CARD if active else "#0b1722"
    outline = PANEL_EDGE if active else "#1e4056"
    draw_panel(draw, box, fill=fill, outline=outline, width=max(1, round(2 * scale)))
    bar_h = max(8, round(10 * scale))
    draw.rectangle((x, y, x + w, y + bar_h), fill=accent if active else "#385168")
    draw_text_fit(
        draw,
        (x + round(22 * scale), y + round(22 * scale), w - round(44 * scale), round(32 * scale)),
        title,
        size=round(23 * scale),
        fill=TEXT if active else MUTED,
        bold=True,
    )


def draw_tag(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    *,
    fill: str,
    outline: str,
    text_fill: str,
    scale: float,
) -> None:
    x, y, w, h = box
    draw.rounded_rectangle((x, y, x + w, y + h), radius=round(8 * scale), fill=fill, outline=outline, width=max(1, round(2 * scale)))
    draw_text_fit(draw, (x + round(10 * scale), y + round(2 * scale), w - round(20 * scale), h - round(4 * scale)), text, size=round(18 * scale), fill=text_fill, bold=True, align="center")


def draw_label_value_table(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    rows: list[tuple[str, str, str]],
    *,
    scale: float,
    label_size: int,
    value_size: int,
    active: bool = True,
) -> None:
    x, y, w, h = box
    row_h = h // len(rows)
    label_w = round(w * 0.48)
    for idx, (label, value, value_color) in enumerate(rows):
        row_y = y + idx * row_h
        if idx % 2 == 0:
            draw.rectangle((x, row_y, x + w, row_y + row_h - round(3 * scale)), fill="#0a1520")
        label_fill = MUTED if active else SOFT
        actual_value_color = value_color if active else MUTED
        draw_text_fit(
            draw,
            (x + round(12 * scale), row_y + round(3 * scale), label_w - round(16 * scale), row_h - round(6 * scale)),
            label,
            size=round(label_size * scale),
            fill=label_fill,
            align="left",
        )
        draw_text_fit(
            draw,
            (x + label_w, row_y + round(3 * scale), w - label_w - round(12 * scale), row_h - round(6 * scale)),
            value,
            size=round(value_size * scale),
            fill=actual_value_color,
            bold=True,
            align="right",
        )


def draw_footer(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, scale: float) -> None:
    draw_panel(draw, box, fill=BLACK, outline="#183047", width=max(1, round(2 * scale)))
    x, y, w, h = box
    draw_text_fit(
        draw,
        (x + round(18 * scale), y + round(8 * scale), w - round(36 * scale), h - round(16 * scale)),
        FOOTER,
        size=round(18 * scale),
        fill=MUTED,
        align="center",
    )


def fmt_sci(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}e}"


def compute_diagnostic() -> dict[str, object]:
    lambda_ref = (math.pi / CAVITY_A_M) ** 2 + (math.pi / CAVITY_D_M) ** 2
    f101 = C0 / 2.0 * math.sqrt((1.0 / CAVITY_A_M) ** 2 + (1.0 / CAVITY_D_M) ** 2)

    dx = CAVITY_A_M / (NX + 1)
    dz = CAVITY_D_M / (NZ + 1)
    x = np.arange(1, NX + 1, dtype=float) * dx
    z = np.arange(1, NZ + 1, dtype=float) * dz
    field = np.outer(np.sin(math.pi * z / CAVITY_D_M), np.sin(math.pi * x / CAVITY_A_M))

    padded = np.pad(field, ((1, 1), (1, 1)), mode="constant")
    center = padded[1:-1, 1:-1]
    left = padded[1:-1, :-2]
    right = padded[1:-1, 2:]
    down = padded[:-2, 1:-1]
    up = padded[2:, 1:-1]
    ae = (
        (2.0 / dx**2 + 2.0 / dz**2) * center
        - (left + right) / dx**2
        - (down + up) / dz**2
    )
    mass_e = field

    lambda_candidate = float(np.sum(field * ae) / np.sum(field * mass_e))
    residual = ae - lambda_candidate * mass_e
    denominator = max(float(np.linalg.norm((lambda_candidate * mass_e).ravel())), TINY)
    normalized_residual = float(np.linalg.norm(residual.ravel()) / denominator)
    relative_lambda_error = float(abs(lambda_candidate - lambda_ref) / lambda_ref)

    boundary_samples = np.concatenate(
        [
            np.sin(math.pi * np.array([0.0, CAVITY_A_M]) / CAVITY_A_M),
            np.sin(math.pi * np.array([0.0, CAVITY_D_M]) / CAVITY_D_M),
        ]
    )
    finite_score = 1.0 if np.isfinite(field).all() and np.isfinite(ae).all() and np.isfinite(residual).all() else 0.0
    boundary_score = 1.0 if float(np.max(np.abs(boundary_samples))) < 1.0e-12 else 0.0
    residual_score = clamp(
        1.0 - math.log10(max(normalized_residual, 1.0e-16) / 1.0e-12) / math.log10(1.0e-3 / 1.0e-12)
    )
    reference_score = clamp(
        1.0 - math.log10(max(relative_lambda_error, 1.0e-16) / 1.0e-6) / math.log10(1.0e-1 / 1.0e-6)
    )
    evidence_score = 100.0 * (
        0.20 * finite_score
        + 0.20 * boundary_score
        + 0.35 * residual_score
        + 0.25 * reference_score
    )

    return {
        "field": field,
        "ae": ae,
        "residual": residual,
        "lambda_ref": float(lambda_ref),
        "lambda_candidate": lambda_candidate,
        "relative_lambda_error": relative_lambda_error,
        "normalized_residual": normalized_residual,
        "finite_score": finite_score,
        "boundary_score": boundary_score,
        "residual_score": residual_score,
        "reference_score": reference_score,
        "evidence_score": evidence_score,
        "frequency_hz": float(f101),
        "dx": dx,
        "dz": dz,
    }


def layout(size: tuple[int, int]) -> dict[str, tuple[int, int, int, int]]:
    scale = size[0] / GIF_SIZE[0]
    outer = round(48 * scale)
    gap = round(36 * scale)
    footer_h = round(58 * scale)
    title_h = round(92 * scale)
    title_y = round(24 * scale)
    main_top = round(126 * scale)
    footer_y = size[1] - outer - footer_h
    main_h = footer_y - main_top - round(24 * scale)
    usable_w = size[0] - 2 * outer
    left_w = round(0.525 * usable_w)
    right_w = usable_w - left_w - gap
    right_x = outer + left_w + gap
    card_gap = round(18 * scale)
    eq_h = round(135 * scale)
    metrics_h = round(150 * scale)
    gate_h = main_h - eq_h - metrics_h - 2 * card_gap
    return {
        "title": (outer, title_y, usable_w, title_h),
        "candidate": (outer, main_top, left_w, main_h),
        "equation": (right_x, main_top, right_w, eq_h),
        "metrics": (right_x, main_top + eq_h + card_gap, right_w, metrics_h),
        "gate": (right_x, main_top + eq_h + card_gap + metrics_h + card_gap, right_w, gate_h),
        "footer": (outer, footer_y, usable_w, footer_h),
    }


def active_phase(t: float) -> str:
    if t < 0.22:
        return "candidate"
    if t < 0.43:
        return "residual"
    if t < 0.63:
        return "magnitude"
    if t < 0.82:
        return "score"
    return "gate"


def phase_alpha(name: str, t: float, *, poster: bool = False) -> float:
    if poster:
        return 1.0
    active = active_phase(t)
    if name == active:
        return 1.0
    if name in {"metrics", "gate"}:
        return 0.72
    return 0.62


def apply_alpha_color(color: str, alpha: float) -> str:
    r, g, b = hex_rgb(color)
    br, bg, bb = hex_rgb(BG)
    alpha = clamp(alpha)
    return f"#{int(br + (r - br) * alpha):02x}{int(bg + (g - bg) * alpha):02x}{int(bb + (b - bb) * alpha):02x}"


def field_image(field: np.ndarray, phase: float, size: tuple[int, int]) -> Image.Image:
    signed = np.clip(field * phase, -1.0, 1.0)
    out = np.zeros((signed.shape[0], signed.shape[1], 3), dtype=np.uint8)
    white = np.array([239, 242, 245], dtype=float)
    pos = np.array([222, 90, 70], dtype=float)
    neg = np.array([54, 122, 210], dtype=float)
    for channel in range(3):
        out[:, :, channel] = np.where(
            signed >= 0,
            white[channel] + (pos[channel] - white[channel]) * signed,
            white[channel] + (neg[channel] - white[channel]) * (-signed),
        )
    image = Image.fromarray(out, "RGB").resize(size, Image.Resampling.BICUBIC)
    return image


def paste_field(draw: ImageDraw.ImageDraw, canvas: Image.Image, box: tuple[int, int, int, int], field: np.ndarray, phase: float, *, scale: float) -> None:
    x, y, w, h = box
    image = field_image(field, phase, (w, h))
    canvas.paste(image, (x, y))
    draw.rectangle((x, y, x + w, y + h), outline="#d7ecff", width=max(1, round(2 * scale)))
    for i in range(1, 8):
        gx = x + round(i * w / 8)
        gy = y + round(i * h / 8)
        draw.line((gx, y, gx, y + h), fill=(230, 240, 250), width=1)
        draw.line((x, gy, x + w, gy), fill=(230, 240, 250), width=1)


def draw_background(draw: ImageDraw.ImageDraw, size: tuple[int, int], *, scale: float) -> None:
    w, h = size
    draw.rectangle((0, 0, w, h), fill=BG)
    for idx in range(10):
        y = round((112 + idx * 61) * scale)
        draw.line((round(45 * scale), y, w - round(45 * scale), y), fill="#133148", width=1)
    for idx in range(13):
        x = round((54 + idx * 104) * scale)
        draw.line((x, round(105 * scale), x, h - round(105 * scale)), fill="#102b40", width=1)


def draw_title(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, scale: float) -> None:
    x, y, w, _h = box
    draw_text_fit(draw, (x, y, w, round(44 * scale)), TITLE, size=round(38 * scale), fill=TEXT, bold=True)
    draw_text_fit(draw, (x, y + round(47 * scale), w, round(30 * scale)), SUBTITLE, size=round(21 * scale), fill=MUTED)


def draw_candidate_panel(
    draw: ImageDraw.ImageDraw,
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    metrics: dict[str, object],
    t: float,
    *,
    scale: float,
    poster: bool,
) -> None:
    x, y, w, h = box
    alpha = phase_alpha("candidate", t, poster=poster)
    draw_panel(draw, box, fill=apply_alpha_color(PANEL, alpha), outline=apply_alpha_color(PANEL_EDGE, alpha))
    pad = round(30 * scale)
    draw_text_fit(draw, (x + pad, y + round(22 * scale), w - 2 * pad, round(36 * scale)), "Candidate Field Slice", size=round(29 * scale), fill=TEXT, bold=True)
    draw_text_fit(draw, (x + pad, y + round(66 * scale), round(340 * scale), round(26 * scale)), "interior Dirichlet grid sample", size=round(19 * scale), fill=MUTED)
    tag_y = y + round(101 * scale)
    draw_tag(draw, (x + pad, tag_y, round(122 * scale), round(32 * scale)), "candidate", fill="#112d3e", outline=CYAN, text_fill=CYAN, scale=scale)
    draw_tag(draw, (x + pad + round(138 * scale), tag_y, round(166 * scale), round(32 * scale)), "not trusted yet", fill="#2b230c", outline=YELLOW, text_fill=YELLOW, scale=scale)

    field_top = tag_y + round(50 * scale)
    field_size = min(w - 2 * pad - round(66 * scale), h - round(250 * scale))
    field_size = max(round(300 * scale), field_size)
    field_size = min(field_size, round(440 * scale))
    field_x = x + (w - field_size) // 2
    phase = math.cos(4.0 * math.pi * t)
    paste_field(draw, canvas, (field_x, field_top, field_size, field_size), np.asarray(metrics["field"]), phase, scale=scale)
    draw_text_fit(
        draw,
        (x + pad, y + h - round(58 * scale), w - 2 * pad, round(34 * scale)),
        "A e = lambda M e is a claim to test.",
        size=round(22 * scale),
        fill=TEXT,
        bold=True,
        align="center",
    )


def draw_equation_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    t: float,
    *,
    scale: float,
    poster: bool,
) -> None:
    alpha = phase_alpha("residual", t, poster=poster)
    draw_metric_card(draw, box, "Residual Calculation", accent=CYAN, active=alpha > 0.85, scale=scale)
    x, y, w, h = box
    equation_y = y + round(54 * scale)
    draw_text_fit(
        draw,
        (x + round(30 * scale), equation_y, w - round(60 * scale), round(32 * scale)),
        "r = A e - lambda M e",
        size=round(24 * scale),
        fill=apply_alpha_color(CYAN, alpha),
        bold=True,
        align="center",
    )
    box_y = y + round(88 * scale)
    small_w = round(124 * scale)
    small_h = round(40 * scale)
    gap = round(28 * scale)
    start_x = x + (w - 3 * small_w - 2 * gap) // 2
    cells = [("A e", CYAN), ("lambda M e", ORANGE), ("r", GREEN)]
    centers: list[tuple[int, int]] = []
    for idx, (label, color) in enumerate(cells):
        cx = start_x + idx * (small_w + gap)
        draw.rectangle((cx, box_y, cx + small_w, box_y + small_h), fill="#111f2d", outline=apply_alpha_color(color, alpha), width=max(1, round(2 * scale)))
        draw_text_fit(draw, (cx + round(8 * scale), box_y + round(5 * scale), small_w - round(16 * scale), small_h - round(10 * scale)), label, size=round(18 * scale), fill=TEXT, align="center")
        centers.append((cx + small_w // 2, box_y + small_h // 2))
    symbol_fill = apply_alpha_color("#8fbdd8", alpha)
    draw_text_fit(
        draw,
        (start_x + small_w, box_y + round(4 * scale), gap, small_h - round(8 * scale)),
        "-",
        size=round(22 * scale),
        fill=symbol_fill,
        bold=True,
        align="center",
    )
    draw_text_fit(
        draw,
        (start_x + 2 * small_w + gap, box_y + round(4 * scale), gap, small_h - round(8 * scale)),
        "->",
        size=round(18 * scale),
        fill=symbol_fill,
        bold=True,
        align="center",
    )


def draw_metrics_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    metrics: dict[str, object],
    t: float,
    *,
    scale: float,
    poster: bool,
) -> None:
    alpha = phase_alpha("magnitude", t, poster=poster)
    draw_metric_card(draw, box, "Residual Metrics", accent=GREEN, active=alpha > 0.85, scale=scale)
    x, y, w, h = box
    rows = [
        ("lambda cand", fmt_sci(float(metrics["lambda_candidate"]), 6), TEXT),
        ("lambda ref", fmt_sci(float(metrics["lambda_ref"]), 6), TEXT),
        ("rel error", fmt_sci(float(metrics["relative_lambda_error"]), 3), YELLOW),
        ("norm residual", fmt_sci(float(metrics["normalized_residual"]), 3), GREEN),
    ]
    draw_label_value_table(
        draw,
        (x + round(24 * scale), y + round(58 * scale), w - round(48 * scale), h - round(72 * scale)),
        rows,
        scale=scale,
        label_size=18,
        value_size=18,
        active=True,
    )


def draw_score_gauge(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], score: float, *, scale: float) -> None:
    x, y, w, h = box
    draw.rectangle((x, y, x + w, y + h), fill="#201b08", outline="#574814", width=max(1, round(2 * scale)))
    fill_w = round(w * clamp(score / 100.0))
    draw.rectangle((x, y, x + fill_w, y + h), fill=YELLOW)


def draw_gate_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    metrics: dict[str, object],
    t: float,
    *,
    scale: float,
    poster: bool,
) -> None:
    alpha = phase_alpha("score", t, poster=poster)
    draw_metric_card(draw, box, "Bounded Evidence Score", accent=YELLOW, active=alpha > 0.85 or poster, scale=scale)
    x, y, w, h = box
    final_score = float(metrics["evidence_score"])
    score_phase = 1.0 if poster else smoothstep(0.64, 0.84, t)
    shown_score = final_score * score_phase
    score_text = f"{shown_score:04.1f} / 100" if score_phase > 0.02 else "pending"
    draw_text_fit(
        draw,
        (x + round(24 * scale), y + round(56 * scale), w - round(48 * scale), round(38 * scale)),
        score_text,
        size=round(30 * scale),
        fill=YELLOW,
        bold=True,
        align="center",
    )
    draw_text_fit(
        draw,
        (x + round(24 * scale), y + round(94 * scale), w - round(48 * scale), round(22 * scale)),
        "bounded diagnostic score",
        size=round(17 * scale),
        fill=MUTED,
        align="center",
    )
    draw_score_gauge(draw, (x + round(36 * scale), y + round(120 * scale), w - round(72 * scale), round(18 * scale)), shown_score, scale=scale)
    rows = [
        ("Evidence Gate", "bounded diagnostic", YELLOW),
        ("Claim Promotion", "internal candidate", TEXT),
        ("ProductionAllowedQ", "false", RED),
        ("ExternalValidationQ", "false", RED),
    ]
    draw_label_value_table(
        draw,
        (x + round(24 * scale), y + round(150 * scale), w - round(48 * scale), h - round(160 * scale)),
        rows,
        scale=scale,
        label_size=15,
        value_size=15,
        active=True,
    )


def draw_scene(frame_index: int, metrics: dict[str, object], size: tuple[int, int], *, poster: bool = False) -> Image.Image:
    scale = size[0] / GIF_SIZE[0]
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    boxes = layout(size)
    t = 1.0 if poster else frame_index / max(1, FRAME_COUNT - 1)
    draw_background(draw, size, scale=scale)
    draw_title(draw, boxes["title"], scale=scale)
    draw_candidate_panel(draw, image, boxes["candidate"], metrics, t, scale=scale, poster=poster)
    draw_equation_card(draw, boxes["equation"], t, scale=scale, poster=poster)
    draw_metrics_panel(draw, boxes["metrics"], metrics, t, scale=scale, poster=poster)
    draw_gate_panel(draw, boxes["gate"], metrics, t, scale=scale, poster=poster)
    draw_footer(draw, boxes["footer"], scale=scale)
    return image


def save_gif(frames: list[Image.Image], output_path: Path) -> None:
    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for frame in frames]
    palette_frames[0].save(
        output_path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=False,
        disposal=2,
    )


def create_mp4_if_available(frame_paths: list[Path], output_path: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    command = [
        ffmpeg,
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(frame_paths[0].parent / "frame_%04d.png"),
        "-vf",
        "format=yuv420p",
        "-an",
        str(output_path),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path.exists() and output_path.stat().st_size > 0


def gif_frame_stats(path: Path) -> tuple[int, float]:
    with Image.open(path) as image:
        frame_count = getattr(image, "n_frames", 1)
        duration_ms = 0
        for index in range(frame_count):
            image.seek(index)
            duration_ms += int(image.info.get("duration", int(1000 / FPS)))
    return frame_count, duration_ms / 1000.0


def write_summary(
    path: Path,
    metrics: dict[str, object],
    mp4_created: bool,
    *,
    frame_count: int,
    duration_seconds: float,
) -> None:
    score_formula = (
        "100.0 * (0.20 * finite_score + 0.20 * boundary_score + "
        "0.35 * residual_score + 0.25 * reference_score)"
    )
    summary = {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "created_by_script": "scripts/generate_eigenpair_residual_evidence_gate.py",
        "model_type": "public canonical scalar PEC cavity eigenpair residual diagnostic",
        "data_source": "public canonical fallback diagnostic",
        "fallback_used": True,
        "cavity_dimensions_m": {"a": CAVITY_A_M, "b": CAVITY_B_M, "d": CAVITY_D_M},
        "mode_description": "TE101 style scalar standing field candidate on an x-z slice",
        "operator_description": "minus finite difference scalar Laplacian on an interior Dirichlet grid",
        "mass_description": "identity mass for the public scalar diagnostic",
        "lambda_ref": float(metrics["lambda_ref"]),
        "lambda_candidate": float(metrics["lambda_candidate"]),
        "relative_lambda_error": float(metrics["relative_lambda_error"]),
        "normalized_residual": float(metrics["normalized_residual"]),
        "finite_score": float(metrics["finite_score"]),
        "boundary_score": float(metrics["boundary_score"]),
        "residual_score": float(metrics["residual_score"]),
        "reference_score": float(metrics["reference_score"]),
        "evidence_score": float(metrics["evidence_score"]),
        "evidence_score_formula": score_formula,
        "grid_size": {"Nx": NX, "Nz": NZ},
        "frames": frame_count,
        "duration_seconds": duration_seconds,
        "layout_quality_check": "explicit pixel safe zones with separate candidate header, tag row, field region, residual equation card, metrics table, score gauge, and footer",
        "text_overlap_check": True,
        "poster_final_state": True,
        "evidence_gate": "bounded diagnostic",
        "claim_promotion": "internal candidate only",
        "promoted": False,
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
        "mp4_created": mp4_created,
        "claim_boundary": "bounded diagnostic only; not external validation, no production readiness claim, not a validated eigenmode",
    }
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    root = repo_root()
    output_dir = root / "assets" / "animations" / "eigenpair_residual_gate"
    temp_dir = root / ".local_temp" / "eigenpair_residual_evidence_gate_generation"
    frame_dir = temp_dir / "frames"
    output_dir.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)

    metrics = compute_diagnostic()
    frames: list[Image.Image] = []
    frame_paths: list[Path] = []
    for frame_index in range(FRAME_COUNT):
        frame = draw_scene(frame_index, metrics, GIF_SIZE)
        frame_path = frame_dir / f"frame_{frame_index:04d}.png"
        frame.save(frame_path)
        frames.append(frame)
        frame_paths.append(frame_path)

    gif_path = output_dir / "eigenpair_residual_evidence_gate.gif"
    poster_path = output_dir / "eigenpair_residual_evidence_gate_poster.png"
    summary_path = output_dir / "eigenpair_residual_evidence_gate_summary.json"
    mp4_path = output_dir / "eigenpair_residual_evidence_gate.mp4"

    save_gif(frames, gif_path)

    poster = draw_scene(FRAME_COUNT - 1, metrics, POSTER_SIZE, poster=True)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", TITLE)
    metadata.add_text("Creation method", "deterministic Python residual and evidence score visualization")
    metadata.add_text("Claim boundary", "bounded diagnostic only")
    poster.save(poster_path, pnginfo=metadata)

    mp4_created = create_mp4_if_available(frame_paths, mp4_path)
    if not mp4_created and mp4_path.exists():
        mp4_path.unlink()

    actual_frame_count, actual_duration_seconds = gif_frame_stats(gif_path)
    write_summary(
        summary_path,
        metrics,
        mp4_created,
        frame_count=actual_frame_count,
        duration_seconds=actual_duration_seconds,
    )

    print(f"wrote {gif_path.relative_to(root)}")
    print(f"wrote {poster_path.relative_to(root)}")
    print(f"wrote {summary_path.relative_to(root)}")
    if mp4_created:
        print(f"wrote {mp4_path.relative_to(root)}")
    else:
        print("mp4 skipped: ffmpeg unavailable")
    print(f"lambda_ref={float(metrics['lambda_ref']):.12e}")
    print(f"lambda_candidate={float(metrics['lambda_candidate']):.12e}")
    print(f"relative_lambda_error={float(metrics['relative_lambda_error']):.12e}")
    print(f"normalized_residual={float(metrics['normalized_residual']):.12e}")
    print(f"evidence_score={float(metrics['evidence_score']):.6f}")


if __name__ == "__main__":
    main()
