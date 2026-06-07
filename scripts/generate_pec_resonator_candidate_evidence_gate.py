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
from matplotlib.collections import PolyCollection
from PIL import Image, PngImagePlugin


TITLE = "PEC Resonator Candidate Evidence Gate"
SUBTITLE = "Analytic TE101 cavity reference with a discrete residual check"
FOOTER = "bounded diagnostic - analytic PEC reference, no external validation or production claim"
FIELD_FORMULA = "Ey(x,y,z,t) = sin(pi x/a) sin(pi z/d) cos(omega t)"
FIELD_FORMULA_SHORT = "Ey = sin(pi x/a) sin(pi z/d) cos(omega t)"
MODE = "TE101 analytic PEC reference"

CAVITY_A_M = 0.080
CAVITY_B_M = 0.084
CAVITY_D_M = 0.084
C0 = 299_792_458.0
NX = 72
NZ = 72
TINY = 1.0e-30

FRAME_COUNT = 144
FPS = 12
DURATION_SECONDS = FRAME_COUNT / FPS
GIF_SIZE = (1280, 720)
POSTER_SIZE = (1600, 900)
DPI = 100

BG = "#061019"
PANEL = "#0c1a27"
PANEL_EDGE = "#294b64"
TEXT = "#e7f1ff"
MUTED = "#9eb4c8"
CYAN = "#55d7ff"
BLUE = "#357bff"
RED = "#ff675f"
GREEN = "#75efb5"
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
    lambda_candidate = float(np.sum(field * ae) / np.sum(field * mass_e))
    residual = ae - lambda_candidate * mass_e
    residual_denominator = max(float(np.linalg.norm((lambda_candidate * mass_e).ravel())), TINY)
    normalized_residual = float(np.linalg.norm(residual.ravel()) / residual_denominator)
    relative_lambda_error = float(abs(lambda_candidate - k2_ref) / k2_ref)

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
    size: int = 13,
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
        zorder=90,
    )


def draw_panel(ax: plt.Axes, xy: tuple[float, float], wh: tuple[float, float], alpha: float = 1.0) -> None:
    x, y = xy
    w, h = wh
    ax.add_patch(
        plt.Rectangle(
            (x, y),
            w,
            h,
            facecolor=PANEL,
            edgecolor=PANEL_EDGE,
            lw=1.1,
            alpha=0.94 * alpha,
            zorder=50,
        )
    )


def camera_angles(t: float) -> tuple[float, float]:
    azimuth = -40.0 + 15.0 * math.sin(2.0 * math.pi * t)
    elevation = 25.0 + 3.0 * math.sin(2.0 * math.pi * t + 0.8)
    return math.radians(azimuth), math.radians(elevation)


def project_points(
    points: np.ndarray,
    azimuth: float,
    elevation: float,
    origin: tuple[float, float] = (0.355, 0.475),
    scale: float = 0.43,
) -> tuple[np.ndarray, np.ndarray]:
    dims = np.array([CAVITY_A_M, CAVITY_B_M, CAVITY_D_M], dtype=float)
    scaled = (points - 0.5) * (dims / np.max(dims))
    cz, sz = math.cos(azimuth), math.sin(azimuth)
    cx, sx = math.cos(elevation), math.sin(elevation)
    rz = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]])
    transformed = scaled @ rz.T @ rx.T
    screen = np.column_stack((origin[0] + scale * transformed[:, 0], origin[1] + scale * transformed[:, 2]))
    depth = transformed[:, 1]
    return screen, depth


def make_field_polygons(
    amplitude: float,
    azimuth: float,
    elevation: float,
) -> tuple[list[np.ndarray], list[tuple[float, float, float, float]], list[float]]:
    nx_vis = 25
    nz_vis = 25
    x_edges = np.linspace(0.0, 1.0, nx_vis + 1)
    z_edges = np.linspace(0.0, 1.0, nz_vis + 1)
    y_slices = [0.22, 0.50, 0.78]
    slice_alphas = [0.52, 0.86, 0.52]
    polygons: list[np.ndarray] = []
    colors: list[tuple[float, float, float, float]] = []
    depths: list[float] = []
    red_base = np.array([1.00, 0.37, 0.30])
    blue_base = np.array([0.20, 0.58, 1.00])
    neutral = np.array([0.78, 0.88, 0.96])

    for y_value, alpha in zip(y_slices, slice_alphas):
        for ix in range(nx_vis):
            for iz in range(nz_vis):
                x0, x1 = x_edges[ix], x_edges[ix + 1]
                z0, z1 = z_edges[iz], z_edges[iz + 1]
                xc = 0.5 * (x0 + x1)
                zc = 0.5 * (z0 + z1)
                value = math.sin(math.pi * xc) * math.sin(math.pi * zc) * amplitude
                corners = np.array(
                    [
                        [x0, y_value, z0],
                        [x1, y_value, z0],
                        [x1, y_value, z1],
                        [x0, y_value, z1],
                    ],
                    dtype=float,
                )
                projected, depth = project_points(corners, azimuth, elevation)
                magnitude = abs(value)
                base = red_base if value >= 0.0 else blue_base
                rgb = neutral * (0.18 * (1.0 - magnitude)) + base * (0.55 + 0.45 * magnitude)
                colors.append((float(rgb[0]), float(rgb[1]), float(rgb[2]), alpha * (0.32 + 0.68 * magnitude)))
                polygons.append(projected)
                depths.append(float(np.mean(depth)))

    order = np.argsort(depths)
    return [polygons[i] for i in order], [colors[i] for i in order], [depths[i] for i in order]


def draw_cavity_edges(ax: plt.Axes, azimuth: float, elevation: float) -> None:
    corners = np.array(
        [
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [1, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
        ],
        dtype=float,
    )
    projected, _ = project_points(corners, azimuth, elevation)
    edges = [
        (0, 1),
        (1, 3),
        (3, 2),
        (2, 0),
        (4, 5),
        (5, 7),
        (7, 6),
        (6, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]
    for start, end in edges:
        ax.plot(
            [projected[start, 0], projected[end, 0]],
            [projected[start, 1], projected[end, 1]],
            color="#b5d7f0",
            lw=1.25,
            alpha=0.75,
            zorder=47,
        )
    for start, end in [(0, 3), (2, 5), (4, 7)]:
        ax.plot(
            [projected[start, 0], projected[end, 0]],
            [projected[start, 1], projected[end, 1]],
            color="#4d7898",
            lw=0.6,
            alpha=0.32,
            zorder=46,
        )


def draw_sample_points(ax: plt.Axes, azimuth: float, elevation: float, alpha: float, amplitude: float) -> None:
    if alpha < 0.02:
        return
    xs = np.linspace(0.10, 0.90, 10)
    zs = np.linspace(0.10, 0.90, 8)
    points = np.array([[x, 0.50, z] for z in zs for x in xs], dtype=float)
    projected, _ = project_points(points, azimuth, elevation)
    values = np.array([math.sin(math.pi * p[0]) * math.sin(math.pi * p[2]) * amplitude for p in points])
    colors = np.where(values >= 0.0, RED, BLUE)
    ax.scatter(
        projected[:, 0],
        projected[:, 1],
        s=14,
        c=colors,
        edgecolors="#eaf5ff",
        linewidths=0.3,
        alpha=0.68 * alpha,
        zorder=48,
    )


def draw_cavity_visual(ax: plt.Axes, metrics: dict[str, object], t: float) -> None:
    ax.add_patch(
        plt.Rectangle(
            (0.035, 0.14),
            0.64,
            0.755,
            facecolor=PANEL,
            edgecolor=PANEL_EDGE,
            lw=1.1,
            alpha=0.94,
            zorder=10,
        )
    )
    azimuth, elevation = camera_angles(t)
    amplitude = math.cos(2.0 * math.pi * 2.0 * t)
    polygons, colors, _depths = make_field_polygons(amplitude, azimuth, elevation)
    collection = PolyCollection(polygons, facecolors=colors, edgecolors=(0.85, 0.93, 1.0, 0.035), linewidths=0.15, zorder=35)
    ax.add_collection(collection)
    draw_sample_points(ax, azimuth, elevation, smoothstep(0.24, 0.44, t), amplitude)
    draw_cavity_edges(ax, azimuth, elevation)
    add_text(ax, 0.060, 0.860, "3D rendered analytic PEC reference", 15, TEXT, weight="bold")
    add_text(ax, 0.060, 0.824, "80 mm x 84 mm x 84 mm", 11, MUTED)
    add_text(ax, 0.060, 0.188, "+ Ey", 11, RED, weight="bold")
    add_text(ax, 0.120, 0.188, "0", 10, MUTED)
    add_text(ax, 0.150, 0.188, "- Ey", 11, BLUE, weight="bold")


def draw_phase_card(ax: plt.Axes, t: float, metrics: dict[str, object]) -> None:
    draw_panel(ax, (0.055, 0.665), (0.345, 0.140), alpha=0.96)
    phase_names = [
        ("Phase 1", "Analytic PEC Reference"),
        ("Phase 2", "Discrete Candidate Grid"),
        ("Phase 3", "Residual Check"),
        ("Phase 4", "Evidence Gate"),
    ]
    phase_index = min(3, int(t * 4.0))
    add_text(ax, 0.075, 0.776, phase_names[phase_index][0], 10, CYAN, weight="bold")
    add_text(ax, 0.155, 0.776, phase_names[phase_index][1], 13, TEXT, weight="bold")
    if phase_index == 0:
        add_text(ax, 0.075, 0.738, FIELD_FORMULA_SHORT, 10, TEXT)
        add_text(ax, 0.075, 0.704, "field pulses with cos(omega t)", 10, MUTED)
    elif phase_index == 1:
        add_text(ax, 0.075, 0.738, "discrete candidate e", 10, TEXT)
        add_text(ax, 0.075, 0.704, "A e = lambda M e", 10, MUTED)
    elif phase_index == 2:
        add_text(ax, 0.075, 0.738, "r = A e - lambda M e", 11, TEXT)
        add_text(ax, 0.075, 0.704, f"norm residual {fmt_sci(float(metrics['normalized_residual']))}", 10, MUTED)
    else:
        add_text(ax, 0.075, 0.738, "Evidence Gate: Candidate / Pending", 11, YELLOW, weight="bold")
        add_text(ax, 0.075, 0.704, "bounded diagnostic only", 10, MUTED)


def draw_metric_group(
    ax: plt.Axes,
    title: str,
    rows: list[tuple[str, str, str]],
    x: float,
    y: float,
    w: float,
    h: float,
    alpha: float,
) -> None:
    ax.add_patch(
        plt.Rectangle(
            (x, y),
            w,
            h,
            facecolor="#0a1521",
            edgecolor="#1f3d54",
            lw=0.8,
            alpha=0.70,
            zorder=55,
        )
    )
    add_text(ax, x + 0.012, y + h - 0.030, title, 11, CYAN, weight="bold", alpha=alpha)
    row_y = y + h - 0.070
    for label, value, color in rows:
        add_text(ax, x + 0.012, row_y, label, 8.5, MUTED, alpha=alpha)
        add_text(ax, x + w - 0.012, row_y, value, 8.5, color, ha="right", alpha=alpha)
        row_y -= 0.042


def draw_evidence_panel(ax: plt.Axes, metrics: dict[str, object], t: float) -> None:
    draw_panel(ax, (0.705, 0.14), (0.265, 0.755))
    add_text(ax, 0.725, 0.855, "Evidence panel", 17, TEXT, weight="bold")
    add_text(ax, 0.725, 0.824, "candidate record, not promotion", 9.5, MUTED)
    values_alpha = smoothstep(0.34, 0.58, t)
    gate_alpha = smoothstep(0.66, 0.84, t)
    draw_metric_group(
        ax,
        "Reference",
        [
            ("f_ref", f"{float(metrics['f101']) / 1.0e9:.6f} GHz", TEXT),
            ("lambda_ref", fmt_sci(float(metrics["k2_ref"])), TEXT),
        ],
        0.725,
        0.675,
        0.225,
        0.120,
        values_alpha,
    )
    draw_metric_group(
        ax,
        "Candidate",
        [
            ("lambda_cand", fmt_sci(float(metrics["lambda_candidate"])), TEXT),
            ("rel error", fmt_sci(float(metrics["relative_lambda_error"])), TEXT),
            ("norm residual", fmt_sci(float(metrics["normalized_residual"])), TEXT),
        ],
        0.725,
        0.492,
        0.225,
        0.158,
        values_alpha,
    )
    draw_metric_group(
        ax,
        "Gate",
        [
            ("Evidence Gate", "Candidate / Pending", YELLOW),
            ("Promoted", "false", RED),
            ("ProductionAllowedQ", "false", RED),
            ("ExternalValidationQ", "false", RED),
        ],
        0.725,
        0.238,
        0.225,
        0.210,
        gate_alpha,
    )


def draw_background(ax: plt.Axes) -> None:
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, zorder=-10))
    for y in np.linspace(0.10, 0.90, 9):
        ax.plot([0.03, 0.97], [y, y], color="#143146", lw=0.55, alpha=0.17, zorder=-5)
    for x in np.linspace(0.04, 0.96, 13):
        ax.plot([x, x], [0.08, 0.92], color="#143146", lw=0.55, alpha=0.13, zorder=-5)


def draw_scene(frame_index: int, metrics: dict[str, object], size: tuple[int, int]) -> Image.Image:
    width, height = size
    fig = plt.figure(figsize=(width / DPI, height / DPI), dpi=DPI, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    t = frame_index / max(1, FRAME_COUNT - 1)
    draw_background(ax)
    add_text(ax, 0.045, 0.950, TITLE, 21, TEXT, weight="bold")
    add_text(ax, 0.045, 0.920, SUBTITLE, 12.5, MUTED)
    draw_cavity_visual(ax, metrics, t)
    draw_phase_card(ax, t, metrics)
    draw_evidence_panel(ax, metrics, t)

    ax.add_patch(plt.Rectangle((0, 0.018), 1.0, 0.045, facecolor="#050a10", edgecolor="#183047", lw=0.8, zorder=70))
    add_text(ax, 0.5, 0.041, FOOTER, 11.5, MUTED, ha="center")

    fig.canvas.draw()
    image = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert("RGB")
    plt.close(fig)
    return image


def save_gif(frames: list[Image.Image], output_path: Path) -> None:
    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for frame in frames]
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


def write_summary(output_path: Path, metrics: dict[str, object], mp4_created: bool) -> None:
    summary = {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "created_by_script": "scripts/generate_pec_resonator_candidate_evidence_gate.py",
        "model_type": "analytic rectangular PEC cavity reference with public finite difference scalar diagnostic",
        "visualization_type": "custom deterministic 3D projected cavity with semi-transparent field slices",
        "cavity_dimensions_m": {"a": CAVITY_A_M, "b": CAVITY_B_M, "d": CAVITY_D_M},
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
        "claim_boundary": "bounded diagnostic only; not external validation, not production readiness, not validated eigenmode",
    }
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


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
