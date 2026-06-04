#!/usr/bin/env python3
"""Generate the public Microwave Cavity Eigenmode Birth showcase animation.

The animation is built from deterministic numerical arrays and Matplotlib
plotting only. It does not use external images, screenshots, or AI imagery.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


TITLE = "Microwave Cavity Eigenmode Birth"
SUBTITLE = "From Yee electric unknowns to a bounded PEC cavity eigenmode residual check"
FOOTER = "bounded internal prototype - no external validation or production claim"
MODE_FORMULA = "Ez(x,y,t) = sin(pi x / Lx) sin(pi y / Ly) cos(omega t)"
MODE_FORMULA_SHORT = "Ez = sin(pi x/Lx) sin(pi y/Ly) cos(omega t)"
GRID_SIZE = {"nx": 72, "ny": 48}
FRAME_COUNT = 120
FPS = 10
DURATION_SECONDS = FRAME_COUNT / FPS
FIGSIZE = (12.8, 7.2)
DPI = 100


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=None,
        help="Optional read-only public-safe summary CSV for residual/reference display.",
    )
    return parser.parse_args()


def read_public_safe_summary(summary_csv: Path | None) -> dict[str, str | bool]:
    summary = {
        "summary_csv_supplied": False,
        "summary_csv_used": False,
        "residual_label": "canonical residual: bounded demo row",
        "reference_label": "analytic PEC reference: canonical rectangular mode",
        "comparison_label": "status: public-safe visualization only",
    }
    if summary_csv is None or not summary_csv.exists():
        return summary

    summary["summary_csv_supplied"] = True
    try:
        with summary_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except UnicodeDecodeError:
        with summary_csv.open("r", encoding="latin-1", newline="") as handle:
            rows = list(csv.DictReader(handle))

    residual_values = [
        row.get("NormalizedResidualValue") or row.get("ResidualValue") or row.get("ResidualNorm")
        for row in rows
    ]
    residual_values = [value for value in residual_values if value not in (None, "")]
    reference_values = [row.get("ReferenceFrequencyHz") for row in rows]
    reference_values = [value for value in reference_values if value not in (None, "")]
    classification = [row.get("ComparisonClassification") for row in rows]
    classification = [value for value in classification if value not in (None, "")]

    if residual_values:
        summary["residual_label"] = f"residual check: {compact_value(residual_values[0])}"
        summary["summary_csv_used"] = True
    else:
        summary["residual_label"] = "residual check: bounded diagnostic row present"
        summary["summary_csv_used"] = True

    if reference_values:
        summary["reference_label"] = f"analytic PEC reference: {compact_value(reference_values[0])} Hz"
    else:
        summary["reference_label"] = "analytic PEC reference comparison: bounded record"

    if classification:
        summary["comparison_label"] = f"status: {compact_words(classification[0], 28)}"
    else:
        summary["comparison_label"] = "comparison status: bounded internal prototype only"
    return summary


def compact_value(value: str) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return compact_words(str(value), 24)
    if number == 0:
        return "0"
    if abs(number) >= 1.0e4 or abs(number) < 1.0e-3:
        return f"{number:.3e}"
    return f"{number:.6g}"


def compact_words(value: str, limit: int) -> str:
    text = " ".join(value.replace("_", " ").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "."


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if x <= edge0:
        return 0.0
    if x >= edge1:
        return 1.0
    t = (x - edge0) / (edge1 - edge0)
    return t * t * (3.0 - 2.0 * t)


def build_sparse_pattern(nx_edges: int = 26, ny_edges: int = 16) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows: list[int] = []
    cols: list[int] = []
    signs: list[int] = []
    width = nx_edges + 1
    for j in range(ny_edges):
        for i in range(nx_edges):
            row = j * nx_edges + i
            bottom = j * width + i
            right = j * width + i + 1
            top = (j + 1) * width + i
            left = j * width + i
            for col, sign in ((bottom, 1), (right, 1), (top, -1), (left, -1)):
                rows.append(row)
                cols.append(col)
                signs.append(sign)
    rows_array = np.asarray(rows)
    cols_array = np.asarray(cols)
    signs_array = np.asarray(signs)
    order = np.argsort(rows_array * 10_000 + cols_array)
    return rows_array[order], cols_array[order], signs_array[order]


def add_text(ax: plt.Axes, x: float, y: float, text: str, size: int = 11, color: str = "#d9e7ff", **kwargs) -> None:
    ax.text(
        x,
        y,
        text,
        color=color,
        fontsize=size,
        family="DejaVu Sans",
        ha=kwargs.pop("ha", "left"),
        va=kwargs.pop("va", "center"),
        **kwargs,
    )


def draw_grid(ax: plt.Axes, alpha: float) -> None:
    for x in np.linspace(0.06, 0.72, 25):
        ax.plot([x, x], [0.19, 0.83], color="#5d768f", lw=0.45, alpha=0.22 * alpha)
    for y in np.linspace(0.19, 0.83, 17):
        ax.plot([0.06, 0.72], [y, y], color="#5d768f", lw=0.45, alpha=0.22 * alpha)


def draw_edge_unknowns(ax: plt.Axes, alpha: float) -> None:
    xs = np.linspace(0.095, 0.685, 12)
    ys = np.linspace(0.235, 0.785, 8)
    for k, y in enumerate(ys):
        ax.scatter(xs, np.full_like(xs, y), s=10, color="#49c2ff", alpha=alpha * (0.55 + 0.15 * (k % 2)), zorder=5)
    for k, x in enumerate(np.linspace(0.105, 0.675, 11)):
        ax.scatter(np.full_like(ys, x), ys, s=10, marker="s", color="#ffbd5a", alpha=alpha * (0.45 + 0.18 * (k % 2)), zorder=5)


def draw_curl_loops(ax: plt.Axes, alpha: float, phase: float) -> None:
    cells = [(0.22, 0.38), (0.38, 0.55), (0.55, 0.42), (0.48, 0.70)]
    w = 0.095
    h = 0.095
    for idx, (x, y) in enumerate(cells):
        pulse = 0.55 + 0.45 * math.sin(2 * math.pi * phase + idx * 0.9)
        color = "#8df7c9" if idx % 2 == 0 else "#ffcc74"
        ax.add_patch(
            plt.Rectangle(
                (x - w / 2, y - h / 2),
                w,
                h,
                fill=False,
                lw=1.5 + pulse,
                ec=color,
                alpha=alpha,
                zorder=7,
            )
        )
        signs = [("+", x, y + h / 2 + 0.017), ("-", x + w / 2 + 0.017, y), ("+", x, y - h / 2 - 0.017), ("-", x - w / 2 - 0.017, y)]
        for sign, sx, sy in signs:
            add_text(ax, sx, sy, sign, size=10, color=color, ha="center", alpha=alpha * (0.7 + 0.3 * pulse), zorder=8)


def draw_sparse_panel(ax: plt.Axes, alpha: float, growth: float, rows: np.ndarray, cols: np.ndarray, signs: np.ndarray) -> None:
    panel = plt.Rectangle((0.755, 0.21), 0.21, 0.55, fill=False, ec="#40546b", lw=1.0, alpha=0.8)
    ax.add_patch(panel)
    add_text(ax, 0.765, 0.79, "bounded prototype structure", size=9, color="#cbd8e8", alpha=alpha)
    count = max(1, int(len(rows) * growth))
    rr = rows[:count]
    cc = cols[:count]
    ss = signs[:count]
    if len(rr):
        x = 0.765 + (cc / max(cols.max(), 1)) * 0.19
        y = 0.235 + (1 - rr / max(rows.max(), 1)) * 0.49
        colors = np.where(ss > 0, "#82f4bd", "#ff9c86")
        ax.scatter(x, y, s=7, c=colors, alpha=0.82 * alpha, linewidths=0, zorder=6)
    for gx in np.linspace(0.765, 0.955, 5):
        ax.plot([gx, gx], [0.235, 0.725], color="#263445", lw=0.4, alpha=0.45 * alpha)
    for gy in np.linspace(0.235, 0.725, 5):
        ax.plot([0.765, 0.955], [gy, gy], color="#263445", lw=0.4, alpha=0.45 * alpha)


def draw_field(ax: plt.Axes, alpha: float, phase: float) -> None:
    nx, ny = GRID_SIZE["nx"], GRID_SIZE["ny"]
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    xx, yy = np.meshgrid(x, y)
    field = np.sin(np.pi * xx) * np.sin(np.pi * yy) * np.cos(2 * np.pi * phase)
    ax.imshow(
        field,
        extent=(0.06, 0.72, 0.19, 0.83),
        origin="lower",
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        interpolation="bilinear",
        alpha=0.78 * alpha,
        zorder=2,
    )
    ax.contour(
        np.linspace(0.06, 0.72, nx),
        np.linspace(0.19, 0.83, ny),
        field,
        levels=np.linspace(-0.75, 0.75, 7),
        colors="#f7fbff",
        linewidths=0.35,
        alpha=0.28 * alpha,
        zorder=3,
    )


def draw_bottom_panel(ax: plt.Axes, summary: dict[str, str | bool], alpha: float) -> None:
    ax.add_patch(plt.Rectangle((0.055, 0.055), 0.91, 0.09, facecolor="#101823", edgecolor="#2b3c50", lw=1.0, alpha=0.86))
    labels = [
        ("residual check", str(summary["residual_label"])),
        ("analytic PEC reference comparison", str(summary["reference_label"])),
        ("bounded internal prototype only", compact_words(str(summary["comparison_label"]), 24)),
    ]
    xs = [0.08, 0.34, 0.66]
    for x, (head, body) in zip(xs, labels):
        add_text(ax, x, 0.116, head, size=8, color="#91a7c0", alpha=alpha)
        add_text(ax, x, 0.080, compact_words(body, 29), size=7, color="#edf6ff", alpha=alpha)


def render_frame(index: int, frame_dir: Path, summary: dict[str, str | bool], sparse: tuple[np.ndarray, np.ndarray, np.ndarray]) -> Path:
    t = index / (FRAME_COUNT - 1)
    phase_unknowns = smoothstep(0.00, 0.24, t) * (1.0 - 0.15 * smoothstep(0.65, 0.75, t))
    phase_loops = smoothstep(0.18, 0.36, t) * (1.0 - smoothstep(0.54, 0.64, t))
    phase_sparse = smoothstep(0.36, 0.62, t)
    phase_field = smoothstep(0.58, 0.75, t)
    field_phase = (t * 1.9) % 1.0

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor("#07101a")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_facecolor("#07101a")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.add_patch(plt.Rectangle((0.045, 0.17), 0.69, 0.67, fill=False, ec="#91a7c0", lw=1.8, alpha=0.95))
    ax.add_patch(plt.Rectangle((0.052, 0.177), 0.676, 0.656, fill=False, ec="#2f4155", lw=0.8, alpha=0.9))
    draw_field(ax, phase_field, field_phase)
    draw_grid(ax, phase_unknowns)
    draw_edge_unknowns(ax, phase_unknowns)
    draw_curl_loops(ax, phase_loops, t * 3.0)
    draw_sparse_panel(ax, max(phase_sparse, 0.25), phase_sparse, *sparse)
    draw_bottom_panel(ax, summary, smoothstep(0.62, 0.78, t))

    add_text(ax, 0.045, 0.935, TITLE, size=19, color="#f4fbff", weight="bold")
    add_text(ax, 0.045, 0.895, SUBTITLE, size=10, color="#9db4cb")

    if t < 0.30:
        stage_text = "Yee electric unknowns"
    elif t < 0.52:
        stage_text = "oriented curl incidence"
    elif t < 0.72:
        stage_text = "bounded curl-curl structure"
    else:
        stage_text = "standing PEC cavity eigenmode slice"
    add_text(ax, 0.06, 0.865, stage_text, size=13, color="#ffffff", weight="bold")

    if t >= 0.70:
        add_text(ax, 0.768, 0.165, "minimal eigenmode path", size=9, color="#d7e5f7")
        add_text(ax, 0.768, 0.150, MODE_FORMULA_SHORT, size=6, color="#90a6bc")

    add_text(ax, 0.5, 0.018, FOOTER, size=8, color="#8ea3b8", ha="center")

    frame_path = frame_dir / f"frame_{index:04d}.png"
    fig.savefig(frame_path, facecolor=fig.get_facecolor(), pad_inches=0.0)
    plt.close(fig)
    return frame_path


def save_gif(frame_paths: list[Path], output_path: Path) -> tuple[int, tuple[int, int]]:
    images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for path in frame_paths]
    first = images[0]
    first.save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=False,
        disposal=2,
    )
    size = first.size
    for image in images:
        image.close()
    with Image.open(output_path) as saved:
        return getattr(saved, "n_frames", len(frame_paths)), saved.size


def save_poster(frame_paths: list[Path], output_path: Path) -> tuple[int, int]:
    poster_source = frame_paths[int(FRAME_COUNT * 0.82)]
    with Image.open(poster_source) as image:
        rgb = image.convert("RGB")
        rgb.save(output_path)
        return rgb.size


def save_mp4_if_available(frame_paths: list[Path], output_path: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
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
        "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "use_metadata_tags",
        "-metadata",
        "title=Microwave Cavity Eigenmode Birth",
        str(output_path),
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path.exists() and output_path.stat().st_size > 0


def write_summary_json(output_path: Path, summary: dict[str, str | bool], gif_frames: int, gif_size: tuple[int, int], mp4_created: bool) -> None:
    payload = {
        "title": TITLE,
        "created_by_script": "scripts/generate_microwave_cavity_eigenmode_birth.py",
        "claim_boundary": "bounded internal prototype visualization only; not external validation, not production readiness, not a qubit simulation",
        "mode_formula_used": MODE_FORMULA,
        "grid_size": GRID_SIZE,
        "frames": gif_frames,
        "gif_dimensions": {"width": gif_size[0], "height": gif_size[1]},
        "duration_seconds": gif_frames / FPS,
        "optional_summary_csv_supplied_at_generation_time": bool(summary["summary_csv_supplied"]),
        "optional_summary_csv_used_at_generation_time": bool(summary["summary_csv_used"]),
        "mp4_created": mp4_created,
        "external_validation_claim": False,
        "production_claim": False,
        "cpml_claim": False,
        "quantum_device_claim": False,
        "external_images_used": False,
        "screenshots_used": False,
        "ai_image_generation_used": False,
        "private_source_code_copied": False,
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = repo_root()
    output_dir = root / "assets" / "animations"
    notes_dir = output_dir / "microwave_cavity_eigenmode_birth"
    temp_dir = root / ".local_temp" / "microwave_cavity_eigenmode_birth_generation"
    frame_dir = temp_dir / "frames"
    notes_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)
    for old_frame in frame_dir.glob("frame_*.png"):
        old_frame.unlink()

    summary = read_public_safe_summary(args.summary_csv)
    sparse = build_sparse_pattern()
    frame_paths = [render_frame(i, frame_dir, summary, sparse) for i in range(FRAME_COUNT)]

    gif_path = output_dir / "microwave_cavity_eigenmode_birth.gif"
    poster_path = output_dir / "microwave_cavity_eigenmode_birth_poster.png"
    summary_path = output_dir / "microwave_cavity_eigenmode_birth_summary.json"
    mp4_path = output_dir / "microwave_cavity_eigenmode_birth.mp4"

    gif_frames, gif_size = save_gif(frame_paths, gif_path)
    save_poster(frame_paths, poster_path)
    mp4_created = save_mp4_if_available(frame_paths, mp4_path)
    write_summary_json(summary_path, summary, gif_frames, gif_size, mp4_created)

    print(f"GIF: {gif_path.relative_to(root)} {gif_size[0]}x{gif_size[1]} frames={gif_frames}")
    print(f"Poster: {poster_path.relative_to(root)}")
    print(f"Summary: {summary_path.relative_to(root)}")
    if mp4_created:
        print(f"MP4: {mp4_path.relative_to(root)}")
    else:
        print("MP4: skipped; ffmpeg unavailable")


if __name__ == "__main__":
    main()
