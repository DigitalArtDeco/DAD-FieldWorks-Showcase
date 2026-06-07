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
from PIL import Image, PngImagePlugin


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
PANEL_EDGE = "#25465f"
TEXT = "#e7f1ff"
MUTED = "#9eb2c5"
CYAN = "#55d7ff"
ORANGE = "#ff9d4d"
RED = "#ff675f"
BLUE = "#3478ff"
GREEN = "#76efb2"
YELLOW = "#ffd166"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return min(hi, max(lo, value))


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if x <= edge0:
        return 0.0
    if x >= edge1:
        return 1.0
    t = (x - edge0) / (edge1 - edge0)
    return t * t * (3.0 - 2.0 * t)


def fmt_sci(value: float, digits: int = 4) -> str:
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
        zorder=40,
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
            zorder=15,
        )
    )


def draw_background(ax: plt.Axes) -> None:
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, zorder=-10))
    for y in np.linspace(0.10, 0.90, 9):
        ax.plot([0.03, 0.97], [y, y], color="#133148", lw=0.55, alpha=0.18, zorder=-5)
    for x in np.linspace(0.04, 0.96, 13):
        ax.plot([x, x], [0.08, 0.92], color="#133148", lw=0.55, alpha=0.14, zorder=-5)


def draw_field_panel(ax: plt.Axes, metrics: dict[str, object], t: float) -> None:
    draw_panel(ax, (0.045, 0.175), (0.38, 0.675))
    add_text(ax, 0.067, 0.815, "Candidate Eigenpair", 17, TEXT, weight="bold")
    phase = math.cos(2.0 * math.pi * (2.0 * t))
    signed = metrics["field"] * phase
    extent = (0.075, 0.395, 0.315, 0.735)
    ax.imshow(
        signed,
        extent=extent,
        origin="lower",
        cmap="RdBu_r",
        vmin=-1.0,
        vmax=1.0,
        interpolation="bilinear",
        alpha=0.90,
        zorder=20,
    )
    ax.add_patch(plt.Rectangle((extent[0], extent[2]), extent[1] - extent[0], extent[3] - extent[2], fill=False, edgecolor="#d7ecff", lw=1.0, alpha=0.8, zorder=30))
    grid_alpha = smoothstep(0.15, 0.35, t)
    for frac in np.linspace(0, 1, 9):
        x = extent[0] + frac * (extent[1] - extent[0])
        y = extent[2] + frac * (extent[3] - extent[2])
        ax.plot([x, x], [extent[2], extent[3]], color="#d9edff", lw=0.35, alpha=0.18 * grid_alpha, zorder=31)
        ax.plot([extent[0], extent[1]], [y, y], color="#d9edff", lw=0.35, alpha=0.18 * grid_alpha, zorder=31)

    if t < 0.42:
        add_text(ax, 0.085, 0.765, "solver candidate", 11, CYAN, alpha=0.95)
        add_text(ax, 0.262, 0.765, "not trusted yet", 11, YELLOW, alpha=0.95)
    else:
        add_text(ax, 0.085, 0.765, "e(x,z) sampled on public grid", 11, MUTED, alpha=0.95)
    add_text(ax, 0.075, 0.265, "A e = lambda M e", 13, TEXT)
    add_text(ax, 0.075, 0.226, "canonical PEC scalar candidate", 10, MUTED)


def draw_residual_panel(ax: plt.Axes, metrics: dict[str, object], t: float) -> None:
    draw_panel(ax, (0.45, 0.175), (0.225, 0.675))
    phase2 = smoothstep(0.20, 0.42, t)
    phase3 = smoothstep(0.42, 0.62, t)
    add_text(ax, 0.47, 0.815, "Residual calculation", 15, TEXT, weight="bold")
    add_text(ax, 0.47, 0.755, "r = A e - lambda M e", 13, CYAN, weight="bold", alpha=0.45 + 0.55 * phase2)

    boxes = [("A e", 0.49, 0.62, CYAN), ("lambda M e", 0.565, 0.53, ORANGE), ("r", 0.535, 0.405, GREEN)]
    for label, x, y, color in boxes:
        ax.add_patch(plt.Rectangle((x, y), 0.095, 0.055, facecolor="#132333", edgecolor=color, lw=1.2, alpha=0.35 + 0.55 * phase2, zorder=18))
        add_text(ax, x + 0.0475, y + 0.028, label, 12, TEXT, ha="center", alpha=phase2)
    ax.plot([0.535, 0.58], [0.62, 0.585], color="#6aa4cc", lw=1.4, alpha=phase2, zorder=20)
    ax.plot([0.61, 0.58], [0.53, 0.585], color="#6aa4cc", lw=1.4, alpha=phase2, zorder=20)
    ax.plot([0.58, 0.58], [0.585, 0.46], color="#6aa4cc", lw=1.4, alpha=phase2, zorder=20)

    residual = np.abs(metrics["residual"])
    sample = residual[::6, ::6]
    sample = sample / max(float(sample.max()), TINY)
    x0, y0, w, h = 0.488, 0.255, 0.15, 0.095
    ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor="#08131d", edgecolor="#284c65", lw=0.9, alpha=phase3, zorder=18))
    for iz in range(sample.shape[0]):
        for ix in range(sample.shape[1]):
            x = x0 + (ix + 0.5) / sample.shape[1] * w
            y = y0 + (iz + 0.5) / sample.shape[0] * h
            ax.scatter(x, y, s=5 + 18 * sample[iz, ix], color=GREEN, alpha=0.18 + 0.65 * phase3 * sample[iz, ix], zorder=22)
    add_text(ax, 0.47, 0.215, "residual vector magnitude map", 10, MUTED, alpha=phase3)


def draw_score_panel(ax: plt.Axes, metrics: dict[str, object], t: float) -> None:
    draw_panel(ax, (0.70, 0.175), (0.255, 0.675))
    phase3 = smoothstep(0.43, 0.62, t)
    phase4 = smoothstep(0.62, 0.82, t)
    add_text(ax, 0.72, 0.815, "Residual magnitude", 15, TEXT, weight="bold")
    add_text(ax, 0.72, 0.755, "residual norm", 9, MUTED, alpha=phase3)
    add_text(ax, 0.93, 0.755, fmt_sci(float(metrics["normalized_residual"])), 9, TEXT, ha="right", alpha=phase3)
    add_text(ax, 0.72, 0.705, "lambda error", 9, MUTED, alpha=phase3)
    add_text(ax, 0.93, 0.705, fmt_sci(float(metrics["relative_lambda_error"])), 9, TEXT, ha="right", alpha=phase3)

    gauge_x, gauge_y, gauge_w, gauge_h = 0.72, 0.62, 0.21, 0.02
    ax.add_patch(plt.Rectangle((gauge_x, gauge_y), gauge_w, gauge_h, facecolor="#17293a", edgecolor="#34536b", lw=0.8, alpha=phase3, zorder=18))
    residual_value = max(float(metrics["normalized_residual"]), 1.0e-16)
    residual_fraction = min(1.0, max(0.03, -math.log10(residual_value) / 16.0))
    ax.add_patch(plt.Rectangle((gauge_x, gauge_y), gauge_w * residual_fraction, gauge_h, facecolor=GREEN, edgecolor="none", alpha=phase3, zorder=21))

    score = float(metrics["evidence_score"])
    animated_score = score * phase4
    add_text(ax, 0.72, 0.545, "Bounded Evidence Score", 12, TEXT, weight="bold", alpha=phase4)
    add_text(ax, 0.93, 0.512, f"{animated_score:04.1f} / 100", 14, YELLOW, ha="right", weight="bold", alpha=phase4)
    ax.add_patch(plt.Rectangle((0.72, 0.475), 0.21, 0.025, facecolor="#201b08", edgecolor="#574814", lw=0.8, alpha=phase4, zorder=18))
    ax.add_patch(plt.Rectangle((0.72, 0.475), 0.21 * animated_score / 100.0, 0.025, facecolor=YELLOW, edgecolor="none", alpha=phase4, zorder=21))

    add_text(ax, 0.72, 0.405, "Claim Gate", 14, TEXT, weight="bold", alpha=phase4)
    gate_lines = [
        ("Gate", "bounded diagnostic"),
        ("Promotion", "internal candidate"),
        ("ProductionAllowedQ", "false"),
        ("ExternalValidationQ", "false"),
    ]
    y = 0.36
    for label, value in gate_lines:
        color = RED if value == "false" else (YELLOW if label == "Gate" else MUTED)
        add_text(ax, 0.72, y, label, 8, MUTED, alpha=phase4)
        add_text(ax, 0.93, y, value, 8, color, ha="right", alpha=phase4)
        y -= 0.047


def draw_flow_labels(ax: plt.Axes, t: float) -> None:
    steps = [
        ("Candidate Eigenpair", 0.065, 0.106),
        ("Residual Calculation", 0.267, 0.106),
        ("Residual Magnitude", 0.475, 0.106),
        ("Bounded Evidence Score", 0.673, 0.106),
        ("Claim Gate", 0.87, 0.106),
    ]
    for idx, (label, x, y) in enumerate(steps):
        active = smoothstep(idx / 5.2, (idx + 1) / 5.2, t)
        color = CYAN if active > 0.5 else MUTED
        add_text(ax, x, y, label, 10, color, ha="center", alpha=0.45 + 0.55 * active)
        if idx < len(steps) - 1:
            ax.plot([x + 0.08, steps[idx + 1][1] - 0.09], [y, y], color="#426783", lw=1.0, alpha=0.35 + 0.55 * active, zorder=16)


def draw_final_message(ax: plt.Axes, t: float) -> None:
    alpha = smoothstep(0.74, 0.86, t)
    if alpha < 0.02:
        return
    draw_panel(ax, (0.42, 0.86), (0.50, 0.052), alpha=alpha)
    add_text(ax, 0.67, 0.895, "DAD checks the claim before promotion.", 15, TEXT, ha="center", weight="bold", alpha=alpha)
    add_text(ax, 0.67, 0.872, "Candidate remains claim bounded.", 10, MUTED, ha="center", alpha=alpha)


def draw_scene(frame_index: int, metrics: dict[str, object], size: tuple[int, int]) -> Image.Image:
    width, height = size
    fig = plt.figure(figsize=(width / DPI, height / DPI), dpi=DPI, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    t = frame_index / max(1, FRAME_COUNT - 1)
    draw_background(ax)
    add_text(ax, 0.045, 0.948, TITLE, 23, TEXT, weight="bold")
    add_text(ax, 0.045, 0.916, SUBTITLE, 13, MUTED)

    draw_field_panel(ax, metrics, t)
    draw_residual_panel(ax, metrics, t)
    draw_score_panel(ax, metrics, t)
    draw_flow_labels(ax, t)
    draw_final_message(ax, t)

    ax.add_patch(plt.Rectangle((0, 0.018), 1.0, 0.045, facecolor="#050a10", edgecolor="#183047", lw=0.8, zorder=25))
    add_text(ax, 0.5, 0.041, FOOTER, 12, MUTED, ha="center")

    fig.canvas.draw()
    image = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert("RGB")
    plt.close(fig)
    return image


def save_gif(frames: list[Image.Image], output_path: Path) -> None:
    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=112) for frame in frames]
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
        "claim_boundary": "bounded diagnostic only; not external validation, not production readiness, not validated eigenmode",
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
