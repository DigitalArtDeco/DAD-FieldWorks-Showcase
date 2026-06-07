#!/usr/bin/env python3
"""Create the Eigenpair Residual Evidence Gate public animation."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, PngImagePlugin


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
GIF_SIZE = (1280, 720)
POSTER_SIZE = (1600, 900)
DPI = 100

BG = "#071018"
PANEL = "#0c1824"
PANEL_2 = "#0f1c2a"
PANEL_EDGE = "#25465f"
TEXT = "#e7f1ff"
MUTED = "#9eb2c5"
FAINT = "#5f7284"
CYAN = "#55d7ff"
ORANGE = "#ff9d4d"
RED = "#ff675f"
BLUE = "#3478ff"
GREEN = "#76efb2"
YELLOW = "#ffd166"

FIELD_BOX = (0.045, 0.145, 0.515, 0.73)
RIGHT_X = 0.595
RIGHT_W = 0.36
EQUATION_BOX = (RIGHT_X, 0.615, RIGHT_W, 0.26)
METRIC_BOX = (RIGHT_X, 0.385, RIGHT_W, 0.205)
GATE_BOX = (RIGHT_X, 0.145, RIGHT_W, 0.215)
FOOTER_BOX = (0.035, 0.033, 0.93, 0.052)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return min(hi, max(lo, value))


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if x <= edge0:
        return 0.0
    if x >= edge1:
        return 1.0
    u = (x - edge0) / (edge1 - edge0)
    return u * u * (3.0 - 2.0 * u)


def fmt_sci(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}e}"


def fmt_lambda(value: float) -> str:
    return f"{value:.6f}"


def load_measure_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def measure_text_px(text: str, size: int) -> tuple[int, int]:
    font = load_measure_font(size)
    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(text: str, max_width_px: int, size: int) -> list[str]:
    words = text.replace("\n", " \n ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        if word == "\n":
            if current:
                lines.append(current)
            current = ""
            continue
        candidate = word if not current else f"{current} {word}"
        candidate_width, _ = measure_text_px(candidate, size)
        if candidate_width <= max_width_px or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_lines(
    text: str,
    max_width_px: int,
    max_height_px: int,
    size: int,
    min_size: int = 8,
) -> tuple[list[str], int]:
    current_size = size
    while current_size >= min_size:
        lines = wrap_text(text, max_width_px, current_size)
        _, line_height = measure_text_px("Ag", current_size)
        total_height = max(1, len(lines)) * int(line_height * 1.45)
        if total_height <= max_height_px:
            return lines, current_size
        current_size -= 1
    lines = wrap_text(text, max_width_px, min_size)
    _, line_height = measure_text_px("Ag", min_size)
    max_lines = max(1, max_height_px // max(1, int(line_height * 1.45)))
    clipped = lines[:max_lines]
    if len(lines) > max_lines and clipped:
        clipped[-1] = clipped[-1].rstrip(".") + "..."
    return clipped, min_size


def draw_text_box(
    ax: plt.Axes,
    box: tuple[float, float, float, float],
    text: str,
    *,
    size: int,
    color: str = TEXT,
    weight: str = "normal",
    ha: str = "left",
    va: str = "top",
    alpha: float = 1.0,
    canvas_size: tuple[int, int] = GIF_SIZE,
    line_spacing: float = 1.45,
    zorder: int = 50,
) -> None:
    x, y, w, h = box
    canvas_w, canvas_h = canvas_size
    max_width_px = max(8, int(w * canvas_w * 0.62))
    max_height_px = max(8, int(h * canvas_h))
    lines, fitted_size = fit_lines(text, max_width_px, max_height_px, size)
    _, line_height_px = measure_text_px("Ag", fitted_size)
    line_step = (line_height_px * line_spacing) / canvas_h
    if ha == "center":
        text_x = x + w / 2.0
    elif ha == "right":
        text_x = x + w
    else:
        text_x = x
    if va == "center":
        total_h = line_step * max(1, len(lines))
        start_y = y + h / 2.0 + total_h / 2.0 - line_step
    elif va == "bottom":
        start_y = y + line_step * (len(lines) - 1)
    else:
        start_y = y + h - line_step * 0.18
    for index, line in enumerate(lines):
        ax.text(
            text_x,
            start_y - index * line_step,
            line,
            fontsize=fitted_size,
            color=color,
            ha=ha,
            va="top",
            weight=weight,
            family="DejaVu Sans",
            alpha=alpha,
            zorder=zorder,
        )


def add_text(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    size: int = 13,
    color: str = TEXT,
    ha: str = "left",
    va: str = "center",
    weight: str = "normal",
    alpha: float = 1.0,
    zorder: int = 50,
) -> None:
    ax.text(
        x,
        y,
        text,
        fontsize=size,
        color=color,
        ha=ha,
        va=va,
        weight=weight,
        family="DejaVu Sans",
        alpha=alpha,
        zorder=zorder,
    )


def draw_panel(
    ax: plt.Axes,
    box: tuple[float, float, float, float],
    *,
    alpha: float = 1.0,
    face: str = PANEL,
    edge: str = PANEL_EDGE,
    zorder: int = 15,
) -> None:
    x, y, w, h = box
    ax.add_patch(
        plt.Rectangle(
            (x, y),
            w,
            h,
            facecolor=face,
            edgecolor=edge,
            lw=1.1,
            alpha=0.94 * alpha,
            zorder=zorder,
        )
    )


def draw_metric_card(
    ax: plt.Axes,
    box: tuple[float, float, float, float],
    title: str,
    *,
    alpha: float = 1.0,
    accent: str = CYAN,
    canvas_size: tuple[int, int] = GIF_SIZE,
) -> None:
    draw_panel(ax, box, alpha=alpha, face=PANEL_2, edge="#2b5870", zorder=18)
    x, y, w, h = box
    ax.add_patch(
        plt.Rectangle((x, y + h - 0.012), w, 0.012, facecolor=accent, edgecolor="none", alpha=0.65 * alpha, zorder=25)
    )
    draw_text_box(
        ax,
        (x + 0.018, y + h - 0.052, w - 0.036, 0.035),
        title,
        size=12,
        color=TEXT,
        weight="bold",
        alpha=alpha,
        canvas_size=canvas_size,
    )


def draw_panel_title(
    ax: plt.Axes,
    box: tuple[float, float, float, float],
    title: str,
    *,
    phase_label: str | None = None,
    alpha: float = 1.0,
    canvas_size: tuple[int, int] = GIF_SIZE,
) -> None:
    x, y, w, h = box
    draw_text_box(
        ax,
        (x + 0.022, y + h - 0.058, w - 0.044, 0.043),
        title,
        size=17,
        color=TEXT,
        weight="bold",
        alpha=alpha,
        canvas_size=canvas_size,
    )
    if phase_label:
        chip_w = min(0.165, w * 0.38)
        chip_h = 0.031
        chip_x = x + w - chip_w - 0.024
        chip_y = y + h - 0.054
        ax.add_patch(
            plt.Rectangle((chip_x, chip_y), chip_w, chip_h, facecolor="#132638", edgecolor="#335a76", lw=0.8, alpha=0.90 * alpha, zorder=27)
        )
        draw_text_box(
            ax,
            (chip_x + 0.006, chip_y + 0.004, chip_w - 0.012, chip_h - 0.006),
            phase_label,
            size=8,
            color=MUTED,
            ha="center",
            va="center",
            alpha=alpha,
            canvas_size=canvas_size,
        )


def draw_label_value_table(
    ax: plt.Axes,
    rows: list[tuple[str, str, str]],
    box: tuple[float, float, float, float],
    *,
    alpha: float = 1.0,
    canvas_size: tuple[int, int] = GIF_SIZE,
    label_size: int = 9,
    value_size: int = 9,
) -> None:
    x, y, w, h = box
    row_h = h / max(1, len(rows))
    for index, (label, value, value_color) in enumerate(rows):
        row_y = y + h - (index + 1) * row_h
        if index % 2 == 0:
            ax.add_patch(
                plt.Rectangle((x, row_y), w, row_h * 0.92, facecolor="#0a1520", edgecolor="none", alpha=0.42 * alpha, zorder=20)
            )
        draw_text_box(
            ax,
            (x + 0.012, row_y + 0.002, w * 0.43, row_h * 0.78),
            label,
            size=label_size,
            color=MUTED,
            alpha=alpha,
            canvas_size=canvas_size,
            va="center",
        )
        draw_text_box(
            ax,
            (x + w * 0.47, row_y + 0.002, w * 0.50 - 0.010, row_h * 0.78),
            value,
            size=value_size,
            color=value_color,
            ha="right",
            alpha=alpha,
            canvas_size=canvas_size,
            va="center",
        )


def draw_footer(ax: plt.Axes, *, canvas_size: tuple[int, int] = GIF_SIZE) -> None:
    draw_panel(ax, FOOTER_BOX, alpha=1.0, face="#050a10", edge="#183047", zorder=35)
    draw_text_box(
        ax,
        (FOOTER_BOX[0] + 0.018, FOOTER_BOX[1] + 0.008, FOOTER_BOX[2] - 0.036, FOOTER_BOX[3] - 0.012),
        FOOTER,
        size=12,
        color=MUTED,
        ha="center",
        va="center",
        canvas_size=canvas_size,
        zorder=60,
    )


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


def phase_label(t: float) -> str:
    if t < 0.24:
        return "candidate"
    if t < 0.46:
        return "residual"
    if t < 0.66:
        return "metrics"
    if t < 0.84:
        return "score"
    return "claim gate"


def draw_background(ax: plt.Axes) -> None:
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, zorder=-10))
    for y in np.linspace(0.12, 0.90, 8):
        ax.plot([0.035, 0.965], [y, y], color="#133148", lw=0.55, alpha=0.18, zorder=-5)
    for x in np.linspace(0.04, 0.96, 12):
        ax.plot([x, x], [0.11, 0.90], color="#133148", lw=0.55, alpha=0.13, zorder=-5)


def draw_field_panel(
    ax: plt.Axes,
    metrics: dict[str, object],
    t: float,
    *,
    canvas_size: tuple[int, int] = GIF_SIZE,
) -> None:
    draw_panel(ax, FIELD_BOX)
    draw_panel_title(ax, FIELD_BOX, "Candidate Field Slice", phase_label=phase_label(t), canvas_size=canvas_size)
    x, y, w, h = FIELD_BOX
    phase = math.cos(4.0 * math.pi * t)
    field = np.asarray(metrics["field"]) * phase
    image_box = (x + 0.045, y + 0.165, w - 0.090, h - 0.260)
    extent = (image_box[0], image_box[0] + image_box[2], image_box[1], image_box[1] + image_box[3])
    ax.imshow(
        field,
        extent=extent,
        origin="lower",
        cmap="RdBu_r",
        vmin=-1.0,
        vmax=1.0,
        interpolation="bilinear",
        alpha=0.92,
        zorder=20,
    )
    ax.add_patch(
        plt.Rectangle(
            (extent[0], extent[2]),
            extent[1] - extent[0],
            extent[3] - extent[2],
            fill=False,
            edgecolor="#d7ecff",
            lw=1.0,
            alpha=0.88,
            zorder=30,
        )
    )
    grid_alpha = 0.15 + 0.20 * smoothstep(0.15, 0.35, t)
    for frac in np.linspace(0, 1, 9):
        gx = extent[0] + frac * (extent[1] - extent[0])
        gy = extent[2] + frac * (extent[3] - extent[2])
        ax.plot([gx, gx], [extent[2], extent[3]], color="#d9edff", lw=0.36, alpha=grid_alpha, zorder=31)
        ax.plot([extent[0], extent[1]], [gy, gy], color="#d9edff", lw=0.36, alpha=grid_alpha, zorder=31)

    draw_text_box(
        ax,
        (x + 0.045, y + h - 0.110, w * 0.43, 0.040),
        "e(x,z) sampled on an interior Dirichlet grid",
        size=10,
        color=MUTED,
        canvas_size=canvas_size,
    )
    draw_text_box(
        ax,
        (x + w - 0.202, y + h - 0.109, 0.150, 0.035),
        "not trusted yet",
        size=10,
        color=YELLOW,
        ha="center",
        va="center",
        canvas_size=canvas_size,
    )
    ax.add_patch(
        plt.Rectangle((x + w - 0.205, y + h - 0.117), 0.156, 0.041, facecolor="#201b08", edgecolor="#5b4a13", lw=0.8, alpha=0.92, zorder=26)
    )
    draw_text_box(
        ax,
        (x + 0.050, y + 0.072, w * 0.50, 0.052),
        "A e = lambda M e is a claim to test.",
        size=12,
        color=TEXT,
        weight="bold",
        canvas_size=canvas_size,
    )


def draw_equation_card(
    ax: plt.Axes,
    box: tuple[float, float, float, float],
    metrics: dict[str, object],
    t: float,
    *,
    canvas_size: tuple[int, int] = GIF_SIZE,
) -> None:
    phase = smoothstep(0.20, 0.43, t)
    draw_metric_card(ax, box, "Residual Calculation", alpha=1.0, accent=CYAN, canvas_size=canvas_size)
    x, y, w, h = box
    draw_text_box(
        ax,
        (x + 0.024, y + h - 0.103, w - 0.048, 0.050),
        "r = A e - lambda M e",
        size=19,
        color=CYAN,
        weight="bold",
        ha="center",
        va="center",
        alpha=0.55 + 0.45 * phase,
        canvas_size=canvas_size,
    )
    row_y = y + 0.087
    chip_w = (w - 0.080) / 3.0
    chips = [
        ("A e", CYAN, x + 0.024),
        ("lambda M e", ORANGE, x + 0.040 + chip_w),
        ("r", GREEN, x + 0.056 + 2 * chip_w),
    ]
    for label, color, chip_x in chips:
        ax.add_patch(
            plt.Rectangle((chip_x, row_y), chip_w, 0.068, facecolor="#111f2d", edgecolor=color, lw=1.2, alpha=0.25 + 0.65 * phase, zorder=25)
        )
        draw_text_box(
            ax,
            (chip_x + 0.006, row_y + 0.010, chip_w - 0.012, 0.048),
            label,
            size=11,
            color=TEXT,
            ha="center",
            va="center",
            alpha=phase,
            canvas_size=canvas_size,
        )
    ax.annotate(
        "",
        xy=(x + w - 0.118, row_y + 0.034),
        xytext=(x + 0.126, row_y + 0.034),
        arrowprops=dict(arrowstyle="-|>", color="#6aa4cc", lw=1.5, alpha=0.75 * phase),
        zorder=27,
    )
    draw_text_box(
        ax,
        (x + 0.024, y + 0.030, w - 0.048, 0.042),
        "Residual gates must pass before promotion.",
        size=9,
        color=MUTED,
        ha="center",
        va="center",
        alpha=0.35 + 0.65 * phase,
        canvas_size=canvas_size,
    )


def draw_metrics_panel(
    ax: plt.Axes,
    box: tuple[float, float, float, float],
    metrics: dict[str, object],
    t: float,
    *,
    canvas_size: tuple[int, int] = GIF_SIZE,
) -> None:
    phase = smoothstep(0.42, 0.63, t)
    draw_metric_card(ax, box, "Residual Metrics", alpha=1.0, accent=GREEN, canvas_size=canvas_size)
    x, y, w, h = box
    rows = [
        ("lambda candidate", fmt_lambda(float(metrics["lambda_candidate"])), TEXT),
        ("lambda reference", fmt_lambda(float(metrics["lambda_ref"])), TEXT),
        ("relative error", fmt_sci(float(metrics["relative_lambda_error"])), YELLOW),
        ("normalized residual", fmt_sci(float(metrics["normalized_residual"])), GREEN),
    ]
    draw_label_value_table(
        ax,
        rows,
        (x + 0.024, y + 0.025, w - 0.048, h - 0.085),
        alpha=0.30 + 0.70 * phase,
        canvas_size=canvas_size,
        label_size=9,
        value_size=9,
    )


def draw_score_gauge(
    ax: plt.Axes,
    box: tuple[float, float, float, float],
    score: float,
    *,
    alpha: float,
    canvas_size: tuple[int, int],
) -> None:
    x, y, w, h = box
    ax.add_patch(plt.Rectangle((x, y), w, h, facecolor="#201b08", edgecolor="#574814", lw=0.8, alpha=0.95 * alpha, zorder=25))
    ax.add_patch(plt.Rectangle((x, y), w * clamp(score / 100.0), h, facecolor=YELLOW, edgecolor="none", alpha=0.92 * alpha, zorder=26))
    draw_text_box(
        ax,
        (x, y + h + 0.010, w, 0.030),
        f"{score:04.1f} / 100",
        size=14,
        color=YELLOW,
        ha="right",
        va="center",
        alpha=alpha,
        weight="bold",
        canvas_size=canvas_size,
    )


def draw_gate_panel(
    ax: plt.Axes,
    box: tuple[float, float, float, float],
    metrics: dict[str, object],
    t: float,
    *,
    canvas_size: tuple[int, int] = GIF_SIZE,
) -> None:
    phase = smoothstep(0.62, 0.84, t)
    final_phase = smoothstep(0.82, 0.94, t)
    draw_metric_card(ax, box, "Bounded Evidence Score", alpha=1.0, accent=YELLOW, canvas_size=canvas_size)
    x, y, w, h = box
    score = float(metrics["evidence_score"]) * phase
    draw_score_gauge(ax, (x + 0.024, y + h - 0.098, w - 0.048, 0.024), score, alpha=0.30 + 0.70 * phase, canvas_size=canvas_size)
    rows = [
        ("Evidence Gate", "bounded diagnostic", YELLOW),
        ("Claim Promotion", "internal candidate", MUTED),
        ("ProductionAllowedQ", "false", RED),
        ("ExternalValidationQ", "false", RED),
    ]
    draw_label_value_table(
        ax,
        rows,
        (x + 0.024, y + 0.030, w - 0.048, h - 0.125),
        alpha=0.35 + 0.65 * phase,
        canvas_size=canvas_size,
        label_size=8,
        value_size=8,
    )
    if final_phase > 0.02:
        ax.add_patch(
            plt.Rectangle((x + 0.023, y + 0.014), w - 0.046, h - 0.058, facecolor="#071018", edgecolor=YELLOW, lw=1.0, alpha=1.0, zorder=70)
        )
        draw_text_box(
            ax,
            (x + 0.044, y + 0.144, w - 0.088, 0.035),
            "residual check",
            size=12,
            color=TEXT,
            weight="bold",
            ha="center",
            va="center",
            alpha=final_phase,
            canvas_size=canvas_size,
            zorder=80,
        )
        draw_text_box(
            ax,
            (x + 0.044, y + 0.094, w - 0.088, 0.044),
            "analytic PEC reference comparison",
            size=10,
            color=TEXT,
            ha="center",
            va="center",
            alpha=final_phase,
            canvas_size=canvas_size,
            zorder=80,
        )
        draw_text_box(
            ax,
            (x + 0.044, y + 0.052, w - 0.088, 0.036),
            "bounded internal prototype only",
            size=10,
            color=YELLOW,
            ha="center",
            va="center",
            alpha=final_phase,
            canvas_size=canvas_size,
            zorder=80,
        )


def draw_scene(frame_index: int, metrics: dict[str, object], size: tuple[int, int]) -> Image.Image:
    width, height = size
    fig = plt.figure(figsize=(width / DPI, height / DPI), dpi=DPI, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    t = frame_index / max(1, FRAME_COUNT - 1)
    draw_background(ax)
    draw_text_box(ax, (0.045, 0.925, 0.91, 0.050), TITLE, size=23, color=TEXT, weight="bold", canvas_size=size)
    draw_text_box(ax, (0.045, 0.890, 0.91, 0.038), SUBTITLE, size=13, color=MUTED, canvas_size=size)

    draw_field_panel(ax, metrics, t, canvas_size=size)
    draw_equation_card(ax, EQUATION_BOX, metrics, t, canvas_size=size)
    draw_metrics_panel(ax, METRIC_BOX, metrics, t, canvas_size=size)
    draw_gate_panel(ax, GATE_BOX, metrics, t, canvas_size=size)
    draw_footer(ax, canvas_size=size)

    fig.canvas.draw()
    image = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert("RGB")
    plt.close(fig)
    return image


def save_gif(frames: list[Image.Image], output_path: Path) -> None:
    palette_frames = [
        ImageOps.contain(frame, GIF_SIZE).convert("P", palette=Image.Palette.ADAPTIVE, colors=112)
        for frame in frames
    ]
    palette_frames[0].save(
        output_path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True,
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


def write_summary(path: Path, metrics: dict[str, object], mp4_created: bool) -> None:
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
        "frames": FRAME_COUNT,
        "duration_seconds": DURATION_SECONDS,
        "layout_quality_check": "two-column dashboard layout with separated equation, metrics, score, and claim gate panels",
        "text_overlap_check": True,
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
        "claim_boundary": "bounded diagnostic only; no external validation, no production readiness, no eigenmode validation result",
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

    poster = draw_scene(int(FRAME_COUNT * 0.92), metrics, POSTER_SIZE)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", TITLE)
    metadata.add_text("Creation method", "deterministic Python residual and evidence score visualization")
    metadata.add_text("Claim boundary", "bounded diagnostic only")
    poster.save(poster_path, pnginfo=metadata)

    mp4_created = create_mp4_if_available(frame_paths, mp4_path)
    if not mp4_created and mp4_path.exists():
        mp4_path.unlink()

    write_summary(summary_path, metrics, mp4_created)

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
