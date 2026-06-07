#!/usr/bin/env python3
"""Create the PEC Resonator Candidate Evidence Gate public animation."""

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
from PIL import Image, PngImagePlugin


TITLE = "PEC Resonator Candidate Evidence Gate"
SUBTITLE = "Analytic TE101 cavity reference with a discrete residual check"
FOOTER = "bounded diagnostic - analytic PEC reference, no external validation or production claim"
FIELD_FORMULA = "Ey(x,z,t) = sin(pi x/a) sin(pi z/d) cos(omega t)"
FIELD_FORMULA_SHORT = "Ey = sin(pi x/a) sin(pi z/d) cos(omega t)"
MODE = "TE101 analytic PEC reference"

CAVITY_A_M = 0.080
CAVITY_B_M = 0.084
CAVITY_D_M = 0.084
C0 = 299_792_458.0
NX = 72
NZ = 72

FRAME_COUNT = 144
FPS = 12
DURATION_SECONDS = FRAME_COUNT / FPS
GIF_SIZE = (1280, 720)
POSTER_SIZE = (1600, 900)
DPI = 100

BG = "#071018"
PANEL = "#0c1824"
PANEL_EDGE = "#24435a"
TEXT = "#e6f1ff"
MUTED = "#9bb0c4"
CYAN = "#53d6ff"
ORANGE = "#ff9b49"
BLUE = "#2f73ff"
RED = "#ff665f"
GREEN = "#78f2b7"
YELLOW = "#ffd166"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fmt_sci(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}e}"


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if x <= edge0:
        return 0.0
    if x >= edge1:
        return 1.0
    t = (x - edge0) / (edge1 - edge0)
    return t * t * (3.0 - 2.0 * t)


def compute_reference_and_candidate() -> dict[str, object]:
    f101 = C0 / 2.0 * math.sqrt((1.0 / CAVITY_A_M) ** 2 + (1.0 / CAVITY_D_M) ** 2)
    omega = 2.0 * math.pi * f101
    k2_ref = (math.pi / CAVITY_A_M) ** 2 + (math.pi / CAVITY_D_M) ** 2

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
    denominator = float(np.sum(field * mass_e))
    lambda_candidate = float(np.sum(field * ae) / denominator)
    residual = ae - lambda_candidate * mass_e
    residual_denominator = float(np.linalg.norm((lambda_candidate * mass_e).ravel()))
    normalized_residual = float(np.linalg.norm(residual.ravel()) / residual_denominator)
    relative_lambda_error = abs(lambda_candidate - k2_ref) / k2_ref

    return {
        "x": x,
        "z": z,
        "field": field,
        "f101": f101,
        "omega": omega,
        "k2_ref": k2_ref,
        "lambda_candidate": lambda_candidate,
        "relative_lambda_error": relative_lambda_error,
        "normalized_residual": normalized_residual,
        "dx": dx,
        "dz": dz,
    }


def add_text(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    size: int = 14,
    color: str = TEXT,
    ha: str = "left",
    va: str = "center",
    weight: str = "normal",
    alpha: float = 1.0,
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
        zorder=30,
    )


def draw_panel(ax: plt.Axes, xy: tuple[float, float], wh: tuple[float, float], alpha: float = 1.0) -> None:
    x, y = xy
    w, h = wh
    rect = plt.Rectangle(
        (x, y),
        w,
        h,
        facecolor=PANEL,
        edgecolor=PANEL_EDGE,
        lw=1.2,
        alpha=0.93 * alpha,
        zorder=20,
    )
    ax.add_patch(rect)


def project(point: tuple[float, float, float]) -> tuple[float, float]:
    x, y, z = point
    return (0.125 + 0.49 * x + 0.115 * y, 0.225 + 0.48 * z + 0.095 * y)


def draw_wire_cavity(ax: plt.Axes, alpha: float = 1.0) -> None:
    corners = {
        "000": project((0, 0, 0)),
        "100": project((1, 0, 0)),
        "010": project((0, 1, 0)),
        "110": project((1, 1, 0)),
        "001": project((0, 0, 1)),
        "101": project((1, 0, 1)),
        "011": project((0, 1, 1)),
        "111": project((1, 1, 1)),
    }
    edges = [
        ("000", "100"),
        ("100", "110"),
        ("110", "010"),
        ("010", "000"),
        ("001", "101"),
        ("101", "111"),
        ("111", "011"),
        ("011", "001"),
        ("000", "001"),
        ("100", "101"),
        ("110", "111"),
        ("010", "011"),
    ]
    for a, b in edges:
        ax.plot(
            [corners[a][0], corners[b][0]],
            [corners[a][1], corners[b][1]],
            color="#86a8c6",
            lw=1.35,
            alpha=0.62 * alpha,
            zorder=7,
        )
    for a, b in [("000", "110"), ("001", "111"), ("010", "101")]:
        ax.plot(
            [corners[a][0], corners[b][0]],
            [corners[a][1], corners[b][1]],
            color="#315069",
            lw=0.8,
            alpha=0.36 * alpha,
            zorder=6,
        )
    add_text(ax, 0.125, 0.17, "80 mm x 84 mm x 84 mm", 12, MUTED, alpha=alpha)


def draw_field_slice(
    ax: plt.Axes,
    field: np.ndarray,
    frame_phase: float,
    grid_alpha: float,
    candidate_alpha: float,
) -> None:
    amplitude = math.cos(2.0 * math.pi * frame_phase)
    signed = field * amplitude
    extent = (0.13, 0.61, 0.23, 0.70)
    ax.imshow(
        signed,
        extent=extent,
        origin="lower",
        cmap="RdBu_r",
        vmin=-1.0,
        vmax=1.0,
        interpolation="bilinear",
        alpha=0.87,
        zorder=3,
    )
    ax.add_patch(
        plt.Rectangle(
            (extent[0], extent[2]),
            extent[1] - extent[0],
            extent[3] - extent[2],
            fill=False,
            edgecolor="#cce6ff",
            lw=0.8,
            alpha=0.55,
            zorder=9,
        )
    )
    for frac in np.linspace(0.0, 1.0, 9):
        x = extent[0] + frac * (extent[1] - extent[0])
        ax.plot([x, x], [extent[2], extent[3]], color="#d9ecff", lw=0.35, alpha=0.17 * grid_alpha, zorder=10)
    for frac in np.linspace(0.0, 1.0, 9):
        y = extent[2] + frac * (extent[3] - extent[2])
        ax.plot([extent[0], extent[1]], [y, y], color="#d9ecff", lw=0.35, alpha=0.17 * grid_alpha, zorder=10)

    if candidate_alpha > 0.01:
        xs = np.linspace(extent[0] + 0.025, extent[1] - 0.025, 13)
        ys = np.linspace(extent[2] + 0.025, extent[3] - 0.025, 9)
        xx, yy = np.meshgrid(xs, ys)
        local = np.sin(np.pi * (xx - extent[0]) / (extent[1] - extent[0])) * np.sin(
            np.pi * (yy - extent[2]) / (extent[3] - extent[2])
        )
        signs = np.where(local * amplitude >= 0, RED, BLUE)
        ax.scatter(
            xx.ravel(),
            yy.ravel(),
            s=14,
            c=signs.ravel(),
            edgecolors="#f4f8ff",
            linewidths=0.25,
            alpha=0.62 * candidate_alpha,
            zorder=12,
        )


def draw_equation_strip(ax: plt.Axes, t: float, metrics: dict[str, object]) -> None:
    draw_panel(ax, (0.055, 0.77), (0.615, 0.135), alpha=1.0)
    phase_names = [
        ("Phase 1", "Analytic PEC Reference"),
        ("Phase 2", "Discrete Yee Candidate Grid"),
        ("Phase 3", "Residual Check"),
        ("Phase 4", "Evidence Gate"),
    ]
    phase_index = min(3, int(t * 4.0))
    add_text(ax, 0.075, 0.875, phase_names[phase_index][0], 11, CYAN, weight="bold")
    add_text(ax, 0.16, 0.875, phase_names[phase_index][1], 17, TEXT, weight="bold")
    if phase_index == 0:
        add_text(ax, 0.075, 0.832, MODE, 12, MUTED)
        add_text(ax, 0.075, 0.797, FIELD_FORMULA_SHORT, 13, TEXT)
    elif phase_index == 1:
        add_text(ax, 0.075, 0.832, "Discrete candidate field e sampled on public grid", 12, MUTED)
        add_text(ax, 0.075, 0.797, "A e = lambda M e   |   candidate not promoted yet", 13, TEXT)
    elif phase_index == 2:
        add_text(ax, 0.075, 0.832, "Residual check: computed from public finite difference diagnostic", 12, MUTED)
        add_text(
            ax,
            0.075,
            0.797,
            f"normalized residual = {fmt_sci(float(metrics['normalized_residual']))}",
            13,
            TEXT,
        )
    else:
        add_text(ax, 0.075, 0.832, "Evidence Gate: Candidate / Pending", 13, YELLOW, weight="bold")
        add_text(ax, 0.075, 0.797, "bounded analytic and discrete diagnostic only", 13, TEXT)


def draw_evidence_panel(ax: plt.Axes, metrics: dict[str, object], t: float) -> None:
    draw_panel(ax, (0.705, 0.135), (0.255, 0.77), alpha=1.0)
    add_text(ax, 0.728, 0.872, "Evidence panel", 17, TEXT, weight="bold")
    add_text(ax, 0.728, 0.835, "candidate record, not promotion", 10, MUTED)

    lines = [
        ("f_ref", f"{float(metrics['f101']) / 1.0e9:.6f} GHz"),
        ("lambda ref", fmt_sci(float(metrics["k2_ref"]))),
        ("lambda cand", fmt_sci(float(metrics["lambda_candidate"]))),
        ("rel lambda err", fmt_sci(float(metrics["relative_lambda_error"]))),
        ("norm residual", fmt_sci(float(metrics["normalized_residual"]))),
    ]
    values_alpha = smoothstep(0.48, 0.64, t)
    y = 0.775
    for label, value in lines:
        add_text(ax, 0.728, y, label, 9, MUTED, alpha=0.45 + 0.55 * values_alpha)
        add_text(ax, 0.932, y, value, 9, TEXT, ha="right", alpha=values_alpha)
        y -= 0.057

    gate_alpha = smoothstep(0.69, 0.82, t)
    gate_y = 0.425
    ax.add_patch(
        plt.Rectangle(
            (0.728, gate_y),
            0.208,
            0.105,
            facecolor="#201b08",
            edgecolor=YELLOW,
            lw=1.4,
            alpha=0.32 + 0.58 * gate_alpha,
        )
    )
    add_text(ax, 0.744, gate_y + 0.067, "Evidence Gate", 10, YELLOW, weight="bold", alpha=gate_alpha)
    add_text(ax, 0.744, gate_y + 0.035, "Candidate / Pending", 13, TEXT, weight="bold", alpha=gate_alpha)

    status = [
        ("Promoted", "false"),
        ("ProductionAllowedQ", "false"),
        ("ExternalValidationQ", "false"),
    ]
    y = 0.325
    for label, value in status:
        add_text(ax, 0.728, y, label, 10, MUTED, alpha=0.65 + 0.35 * gate_alpha)
        add_text(ax, 0.932, y, value, 11, RED if value == "false" else GREEN, ha="right", alpha=gate_alpha)
        y -= 0.055

    add_text(ax, 0.728, 0.185, "bounded analytic and", 10, MUTED, alpha=gate_alpha)
    add_text(ax, 0.728, 0.158, "discrete diagnostic only", 10, MUTED, alpha=gate_alpha)


def draw_residual_meter(ax: plt.Axes, metrics: dict[str, object], t: float) -> None:
    alpha = smoothstep(0.50, 0.68, t)
    draw_panel(ax, (0.055, 0.08), (0.615, 0.095), alpha=0.9)
    add_text(ax, 0.075, 0.142, "Residual check", 12, CYAN, weight="bold", alpha=alpha)
    bar_x, bar_y, bar_w, bar_h = 0.22, 0.123, 0.39, 0.016
    ax.add_patch(
        plt.Rectangle((bar_x, bar_y), bar_w, bar_h, facecolor="#172635", edgecolor="#34536b", lw=0.8, alpha=alpha)
    )
    residual_value = max(float(metrics["normalized_residual"]), 1.0e-16)
    visible_fraction = min(1.0, max(0.035, -math.log10(residual_value) / 16.0))
    ax.add_patch(
        plt.Rectangle((bar_x, bar_y), bar_w * visible_fraction, bar_h, facecolor=GREEN, edgecolor="none", alpha=alpha)
    )
    add_text(ax, 0.62, 0.131, fmt_sci(float(metrics["normalized_residual"])), 11, TEXT, ha="right", alpha=alpha)
    add_text(ax, 0.075, 0.102, "computed from A e - lambda M e", 10, MUTED, alpha=alpha)


def draw_scene(frame_index: int, metrics: dict[str, object], size: tuple[int, int]) -> Image.Image:
    width, height = size
    fig = plt.figure(figsize=(width / DPI, height / DPI), dpi=DPI, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    t = frame_index / max(1, FRAME_COUNT - 1)
    field_phase = 2.0 * t
    grid_alpha = smoothstep(0.22, 0.38, t)
    candidate_alpha = smoothstep(0.26, 0.44, t)

    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, zorder=-10))
    for y in np.linspace(0.10, 0.90, 9):
        ax.plot([0.03, 0.97], [y, y], color="#143146", lw=0.6, alpha=0.18, zorder=-4)
    for x in np.linspace(0.04, 0.96, 13):
        ax.plot([x, x], [0.08, 0.92], color="#143146", lw=0.6, alpha=0.14, zorder=-4)

    add_text(ax, 0.055, 0.948, TITLE, 22, TEXT, weight="bold")
    add_text(ax, 0.055, 0.916, SUBTITLE, 13, MUTED)

    draw_wire_cavity(ax, alpha=1.0)
    draw_field_slice(ax, metrics["field"], field_phase, grid_alpha, candidate_alpha)
    draw_equation_strip(ax, t, metrics)
    draw_residual_meter(ax, metrics, t)
    draw_evidence_panel(ax, metrics, t)

    if t < 0.45:
        add_text(ax, 0.18, 0.735, "+ Ey", 11, RED, weight="bold", alpha=0.8)
        add_text(ax, 0.48, 0.735, "- Ey", 11, BLUE, weight="bold", alpha=0.8)
    if candidate_alpha > 0.02:
        add_text(ax, 0.155, 0.205, "sampled interior grid", 10, MUTED, alpha=candidate_alpha)
        add_text(ax, 0.36, 0.205, "discrete candidate e", 10, MUTED, alpha=candidate_alpha)

    ax.add_patch(plt.Rectangle((0, 0.018), 1.0, 0.045, facecolor="#050a10", edgecolor="#183047", lw=0.8))
    add_text(ax, 0.5, 0.041, FOOTER, 12, MUTED, ha="center")

    fig.canvas.draw()
    image = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert("RGB")
    plt.close(fig)
    return image


def save_gif(frames: list[Image.Image], output_path: Path) -> None:
    palette_frames = [
        frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
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


def write_summary(output_path: Path, metrics: dict[str, object], mp4_created: bool) -> None:
    summary = {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "created_by_script": "scripts/generate_pec_resonator_candidate_evidence_gate.py",
        "model_type": "analytic rectangular PEC cavity reference with public finite difference scalar diagnostic",
        "cavity_dimensions_m": {
            "a": CAVITY_A_M,
            "b": CAVITY_B_M,
            "d": CAVITY_D_M,
        },
        "mode": "TE101",
        "field_formula": FIELD_FORMULA,
        "frequency_hz": float(metrics["f101"]),
        "frequency_ghz": float(metrics["f101"]) / 1.0e9,
        "lambda_ref": float(metrics["k2_ref"]),
        "lambda_candidate": float(metrics["lambda_candidate"]),
        "relative_lambda_error": float(metrics["relative_lambda_error"]),
        "normalized_residual": float(metrics["normalized_residual"]),
        "grid_size": {"Nx": NX, "Nz": NZ},
        "frames": FRAME_COUNT,
        "duration_seconds": DURATION_SECONDS,
        "evidence_gate": "Candidate / Pending",
        "promoted": False,
        "ProductionAllowedQ": False,
        "ExternalValidationQ": False,
        "external_validation_claim": False,
        "production_claim": False,
        "commercial_solver_equivalence_claim": False,
        "qubit_simulation_claim": False,
        "quantum_device_claim": False,
        "cpml_claim": False,
        "arbitrary_geometry_claim": False,
        "external_images_used": False,
        "screenshots_used": False,
        "generative_image_tools_used": False,
        "private_source_code_copied": False,
        "mp4_created": mp4_created,
        "claim_boundary": "bounded diagnostic only; not external validation, not production readiness, not validated eigenmode",
    }
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def create_mp4_if_available(frame_paths: list[Path], output_path: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    input_pattern = str(frame_paths[0].parent / "frame_%04d.png")
    command = [
        ffmpeg,
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        input_pattern,
        "-vf",
        "format=yuv420p",
        "-an",
        str(output_path),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path.exists() and output_path.stat().st_size > 0


def main() -> None:
    root = repo_root()
    output_dir = root / "assets" / "animations" / "pec_resonator_candidate"
    temp_dir = root / ".local_temp" / "pec_resonator_candidate_evidence_gate_generation"
    frame_dir = temp_dir / "frames"
    output_dir.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)

    metrics = compute_reference_and_candidate()
    frames: list[Image.Image] = []
    frame_paths: list[Path] = []
    for frame_index in range(FRAME_COUNT):
        frame = draw_scene(frame_index, metrics, GIF_SIZE)
        frame_path = frame_dir / f"frame_{frame_index:04d}.png"
        frame.save(frame_path)
        frame_paths.append(frame_path)
        frames.append(frame)

    gif_path = output_dir / "pec_resonator_candidate_evidence_gate.gif"
    poster_path = output_dir / "pec_resonator_candidate_evidence_gate_poster.png"
    summary_path = output_dir / "pec_resonator_candidate_evidence_gate_summary.json"
    mp4_path = output_dir / "pec_resonator_candidate_evidence_gate.mp4"

    save_gif(frames, gif_path)
    poster = draw_scene(int(FRAME_COUNT * 0.78), metrics, POSTER_SIZE)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", TITLE)
    metadata.add_text("Creation method", "deterministic Python analytic and discrete diagnostic generation")
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
    print(f"f_ref_GHz={float(metrics['f101']) / 1.0e9:.9f}")
    print(f"lambda_ref={float(metrics['k2_ref']):.12e}")
    print(f"lambda_candidate={float(metrics['lambda_candidate']):.12e}")
    print(f"relative_lambda_error={float(metrics['relative_lambda_error']):.12e}")
    print(f"normalized_residual={float(metrics['normalized_residual']):.12e}")


if __name__ == "__main__":
    main()
