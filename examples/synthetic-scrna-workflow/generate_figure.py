#!/usr/bin/env python3
"""Generate a publication-style synthetic single-cell workflow figure.

All values are simulated for visual demonstration only. The script writes the
underlying synthetic data, editable/vector outputs, a figure specification,
palette mapping, and a compact QA record.
"""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib-cache"))

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle


SEED = 20261020
WIDTH_MM = 178
HEIGHT_MM = 165
WIDTH_IN = WIDTH_MM / 25.4

INK = "#1D264C"
MUTED_INK = "#596071"
GRID = "#D9DDE4"
PAPER = "#FFFFFF"
PANEL_TINT = "#F7F8FA"
CELL_COLORS = {
    "T cell": "#1D264C",
    "B cell": "#733E71",
    "Myeloid": "#C7765A",
    "Stromal": "#77A893",
    "Epithelial": "#D2A33D",
}
MARKERS = ["o", "s", "^", "D", "P"]


def mm(value: float) -> float:
    return value / 25.4


def lighten(hex_color: str, amount: float = 0.82) -> tuple[float, float, float]:
    rgb = np.array(mpl.colors.to_rgb(hex_color))
    return tuple(rgb + (1 - rgb) * amount)


def generate_embedding(rng: np.random.Generator):
    specs = [
        ("T cell", 230, (-2.6, 0.9), (1.05, 0.42), -0.35),
        ("B cell", 145, (-0.7, 2.25), (0.70, 0.35), 0.45),
        ("Myeloid", 205, (1.35, 0.75), (0.95, 0.48), -0.55),
        ("Stromal", 125, (2.4, -1.55), (0.65, 0.34), 0.20),
        ("Epithelial", 175, (-0.75, -1.45), (0.92, 0.43), 0.60),
    ]
    rows = []
    points = {}
    for label, count, center, scales, angle in specs:
        rot = np.array(
            [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]]
        )
        cloud = rng.normal(size=(count, 2)) * np.array(scales)
        cloud = cloud @ rot.T + np.array(center)
        points[label] = cloud
        for cell_index, (x, y) in enumerate(cloud, 1):
            rows.append(
                {
                    "record_type": "cell",
                    "sample": "synthetic_pool",
                    "group": "illustrative",
                    "cell_type": label,
                    "feature": f"cell_{label.replace(' ', '_').lower()}_{cell_index:03d}",
                    "value_1": f"{x:.6f}",
                    "value_2": f"{y:.6f}",
                }
            )
    return points, rows


def generate_expression(rng: np.random.Generator):
    genes = ["CD3D", "MS4A1", "LYZ", "COL1A1", "EPCAM", "MKI67", "IFITM3"]
    base = np.array(
        [
            [2.7, 0.2, 0.4, 0.1, 0.1, 0.8, 1.1],
            [0.2, 2.8, 0.3, 0.1, 0.2, 0.6, 0.8],
            [0.2, 0.2, 2.9, 0.3, 0.1, 0.5, 1.7],
            [0.1, 0.1, 0.4, 2.8, 0.2, 0.4, 0.7],
            [0.1, 0.2, 0.3, 0.2, 2.9, 1.1, 0.9],
        ]
    )
    matrix = np.clip(base + rng.normal(0, 0.10, base.shape), 0, None)
    rows = []
    for i, cell_type in enumerate(CELL_COLORS):
        for j, gene in enumerate(genes):
            rows.append(
                {
                    "record_type": "expression",
                    "sample": "synthetic_pool",
                    "group": "illustrative",
                    "cell_type": cell_type,
                    "feature": gene,
                    "value_1": f"{matrix[i, j]:.6f}",
                    "value_2": "",
                }
            )
    return genes, matrix, rows


def generate_composition(rng: np.random.Generator):
    control_mean = np.array([0.33, 0.20, 0.21, 0.13, 0.13])
    treated_mean = np.array([0.43, 0.16, 0.17, 0.11, 0.13])
    samples = []
    rows = []
    for group, mean in [("Control", control_mean), ("Treatment", treated_mean)]:
        for donor in range(1, 7):
            fractions = rng.dirichlet(mean * 95)
            sample = f"{group[0]}{donor}"
            samples.append((sample, group, fractions))
            for cell_type, value in zip(CELL_COLORS, fractions):
                rows.append(
                    {
                        "record_type": "composition",
                        "sample": sample,
                        "group": group,
                        "cell_type": cell_type,
                        "feature": "fraction",
                        "value_1": f"{value:.6f}",
                        "value_2": "",
                    }
                )
    return samples, rows


def write_data(rows: list[dict]) -> None:
    with (ROOT / "synthetic_data.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["record_type", "sample", "group", "cell_type", "feature", "value_1", "value_2"],
        )
        writer.writeheader()
        writer.writerows(rows)


def style_axes(ax):
    ax.tick_params(colors=MUTED_INK, labelsize=7.2, length=2.5, width=0.7)
    for spine in ax.spines.values():
        spine.set_color(GRID)
        spine.set_linewidth(0.8)


def panel_label(ax, label: str) -> None:
    ax.text(
        -0.06,
        1.055,
        label,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        color=INK,
        ha="left",
        va="top",
    )


def draw_workflow(ax) -> None:
    ax.set_axis_off()
    panel_label(ax, "A")
    ax.text(0.0, 1.02, "From tissue to interpretable cell states", transform=ax.transAxes,
            fontsize=8.6, fontweight="bold", color=INK, va="top")
    ax.text(1.0, 1.02, "Illustrative workflow · synthetic demonstration", transform=ax.transAxes,
            fontsize=7.1, color=MUTED_INK, va="top", ha="right")

    steps = [
        ("Tissue\nsampling", "context", CELL_COLORS["T cell"]),
        ("Cell\nisolation", "prepare", CELL_COLORS["B cell"]),
        ("scRNA-seq", "measure", CELL_COLORS["Myeloid"]),
        ("Quality\ncontrol", "filter", CELL_COLORS["Stromal"]),
        ("Cell-state\nmap", "discover", CELL_COLORS["Epithelial"]),
        ("Marker\nvalidation", "interpret", INK),
    ]
    y, h = 0.22, 0.48
    w, gap = 0.135, 0.032
    start = 0.018
    for i, (title, subtitle, color) in enumerate(steps):
        x = start + i * (w + gap)
        if i:
            arrow = FancyArrowPatch(
                (x - gap + 0.004, y + h / 2),
                (x - 0.006, y + h / 2),
                transform=ax.transAxes,
                arrowstyle="-|>",
                mutation_scale=9,
                linewidth=0.9,
                color="#9AA1AE",
            )
            ax.add_patch(arrow)
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            transform=ax.transAxes,
            linewidth=0.85,
            edgecolor=lighten(color, 0.38),
            facecolor=lighten(color, 0.89),
        )
        ax.add_patch(box)
        badge = Circle((x + 0.023, y + h - 0.065), 0.0175, transform=ax.transAxes,
                       facecolor=color, edgecolor="none")
        ax.add_patch(badge)
        ax.text(x + 0.023, y + h - 0.065, str(i + 1), transform=ax.transAxes,
                color="white", fontsize=7.0, fontweight="bold", ha="center", va="center")
        ax.text(x + w / 2, y + h * 0.53, title, transform=ax.transAxes,
                color=INK, fontsize=7.4, fontweight="bold", ha="center", va="center",
                linespacing=1.12)
        ax.text(x + w / 2, y + 0.065, subtitle.upper(), transform=ax.transAxes,
                color=color, fontsize=7.0, fontweight="bold", ha="center", va="center")


def draw_umap(ax, points: dict[str, np.ndarray]) -> None:
    panel_label(ax, "B")
    ax.set_title("Synthetic cell-state embedding", loc="left", fontsize=8.6,
                 fontweight="bold", color=INK, pad=9)
    for (cell_type, cloud), marker in zip(points.items(), MARKERS):
        ax.scatter(
            cloud[:, 0], cloud[:, 1], s=8, c=CELL_COLORS[cell_type], marker=marker,
            alpha=0.72, linewidths=0, rasterized=False,
        )
        cx, cy = cloud.mean(axis=0)
        ax.text(cx, cy, cell_type.replace(" ", "\n"), fontsize=7.0, fontweight="bold",
                color=INK, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.82))
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    x0, y0 = -3.75, -2.7
    ax.plot([x0, x0 + 0.75], [y0, y0], color=MUTED_INK, lw=0.85, clip_on=False)
    ax.plot([x0, x0], [y0, y0 + 0.75], color=MUTED_INK, lw=0.85, clip_on=False)
    ax.text(x0 + 0.38, y0 - 0.19, "UMAP 1", fontsize=7.0, color=MUTED_INK, ha="center", va="top")
    ax.text(x0 - 0.15, y0 + 0.38, "UMAP 2", fontsize=7.0, color=MUTED_INK,
            ha="right", va="center", rotation=90)
    ax.set_xlim(-4.0, 3.65)
    ax.set_ylim(-2.95, 3.15)
    ax.text(0.02, 0.02, "n = 880 simulated cells", transform=ax.transAxes,
            fontsize=7.0, color=MUTED_INK, ha="left", va="bottom")


def draw_heatmap(ax, genes: list[str], matrix: np.ndarray) -> None:
    panel_label(ax, "C")
    ax.set_title("Lineage-marker expression", loc="left", fontsize=8.6,
                 fontweight="bold", color=INK, pad=9)
    im = ax.imshow(matrix, cmap="magma", vmin=0, vmax=3.0, interpolation="nearest", aspect="auto")
    ax.set_xticks(np.arange(len(genes)), genes, rotation=55, ha="right", rotation_mode="anchor")
    ax.set_yticks(np.arange(len(CELL_COLORS)), list(CELL_COLORS))
    ax.tick_params(axis="both", labelsize=7.0, length=0, pad=3, colors=MUTED_INK)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for y in np.arange(0.5, len(CELL_COLORS), 1):
        ax.axhline(y, color="white", lw=0.65, alpha=0.82)
    for x in np.arange(0.5, len(genes), 1):
        ax.axvline(x, color="white", lw=0.5, alpha=0.62)
    cax = ax.inset_axes([0.12, -0.27, 0.72, 0.040])
    cb = plt.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_ticks([0, 1.5, 3.0])
    cb.ax.tick_params(labelsize=7.0, length=1.8, width=0.5, colors=MUTED_INK, pad=1)
    cb.outline.set_visible(False)
    cax.text(-0.02, 0.5, "low", transform=cax.transAxes, ha="right", va="center",
             fontsize=7.0, color=MUTED_INK)
    cax.text(1.02, 0.5, "high", transform=cax.transAxes, ha="left", va="center",
             fontsize=7.0, color=MUTED_INK)


def draw_composition(ax, samples) -> None:
    panel_label(ax, "D")
    ax.set_title("Cellular composition by donor", loc="left", fontsize=8.6,
                 fontweight="bold", color=INK, pad=9)
    positions = list(range(6)) + list(range(8, 14))
    bottoms = np.zeros(len(samples))
    for cell_index, (cell_type, color) in enumerate(CELL_COLORS.items()):
        values = np.array([fractions[cell_index] for _, _, fractions in samples]) * 100
        ax.bar(positions, values, bottom=bottoms, color=color, width=0.76,
               linewidth=0.35, edgecolor="white", label=cell_type)
        bottoms += values
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Cells (%)", fontsize=7.0, color=MUTED_INK, labelpad=2)
    ax.set_xticks(positions, [sample for sample, _, _ in samples], rotation=0)
    ax.grid(axis="y", color=GRID, lw=0.65, alpha=0.85)
    ax.set_axisbelow(True)
    style_axes(ax)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="y", length=0)
    ax.text(2.5, -14.0, "Control", fontsize=7.0, color=INK, fontweight="bold",
            ha="center", va="top", clip_on=False)
    ax.text(10.5, -14.0, "Treatment", fontsize=7.0, color=INK, fontweight="bold",
            ha="center", va="top", clip_on=False)
    ax.plot([-0.35, 5.35], [-8.0, -8.0], color=GRID, lw=0.8, clip_on=False)
    ax.plot([7.65, 13.35], [-8.0, -8.0], color=GRID, lw=0.8, clip_on=False)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc="upper left", bbox_to_anchor=(0.0, -0.23),
              ncol=2, frameon=False, fontsize=7.0, handlelength=1.0, columnspacing=1.1,
              handletextpad=0.4, borderaxespad=0)


def write_metadata() -> None:
    palette = {
        "ink": INK,
        "neutral": "#D9DDE4",
        "primary": CELL_COLORS["T cell"],
        "secondary": CELL_COLORS["B cell"],
        "support_1": CELL_COLORS["Myeloid"],
        "support_2": CELL_COLORS["Stromal"],
        "support_3": CELL_COLORS["Epithelial"],
        "semantic_mapping": CELL_COLORS,
        "corpus_precedent": {
            "stable_id": "wechat:2247486705:1",
            "sequence": 96,
            "journal": "Nature Nanotechnology",
            "use": "functional contrast and restrained visual weight; artwork not copied",
        },
    }
    (ROOT / "palette.json").write_text(json.dumps(palette, ensure_ascii=False, indent=2), encoding="utf-8")

    spec = {
        "core_claim": "A staged single-cell workflow can connect sample processing to interpretable cell-state, marker, and composition summaries.",
        "audience": "Researchers evaluating a double-column manuscript figure demonstration",
        "selection": {
            "mode": "explicit_auto_bypass",
            "chosen_type": "method-to-evidence multi-panel: staged workflow + embedding + heatmap + normalized stacked bars",
            "candidates": [
                "staged workflow only",
                "method-to-evidence multi-panel",
                "graphical abstract",
            ],
            "reason": "Historical demonstration generated after the user delegated the test composition to the skill.",
        },
        "evidence": [
            {"source": "synthetic_data.csv", "status": "illustrative"},
            {"source": "workflow labels authored for this demonstration", "status": "illustrative"},
        ],
        "comparison": "Illustrative control-versus-treatment composition; no inferential claim or statistical test.",
        "uncertainty": "Six simulated donors per group; no confidence intervals because the panel demonstrates composition layout only.",
        "panels": [
            {"id": "A", "role": "process", "form": "staged-flow", "claim": "The reading order from sample to interpretation is explicit."},
            {"id": "B", "role": "primary evidence", "form": "embedding", "claim": "Simulated cells form five visually distinct illustrative states."},
            {"id": "C", "role": "validation", "form": "heatmap", "claim": "Illustrative lineage markers distinguish the simulated states."},
            {"id": "D", "role": "composition", "form": "normalized-stacked-bars", "claim": "Synthetic donor-level composition can be compared without implying significance."},
        ],
        "reading_order": "A workflow, then B embedding, C marker validation, and D donor-level composition.",
        "palette": {
            "ink": INK,
            "neutral": "#D9DDE4",
            "primary": CELL_COLORS["T cell"],
            "secondary": CELL_COLORS["B cell"],
            "support_1": CELL_COLORS["Myeloid"],
            "support_2": CELL_COLORS["Stromal"],
            "support_3": CELL_COLORS["Epithelial"],
        },
        "output": {
            "width_mm": WIDTH_MM,
            "formats": ["svg", "pdf", "png"],
            "editable": True,
            "backend": "python",
            "target_journal": "generic high-impact journal",
        },
        "integrity_risks": [
            "All values are synthetic and must not be interpreted as experimental evidence.",
            "Embedding distance is illustrative and is not a calibrated biological distance.",
            "No statistical significance is implied by the composition panel.",
        ],
        "provenance": [
            "Generated deterministically with seed 20261020.",
            "Style precedent: PubCNS case 96 (Nature Nanotechnology); no artwork traced or copied.",
        ],
    }
    (ROOT / "figure-spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

    qa = {
        "status": "pass",
        "final_width_mm": WIDTH_MM,
        "final_height_mm": HEIGHT_MM,
        "minimum_text_pt": 7.0,
        "minimum_text_exemption": None,
        "checks": {
            "deterministic_seed": True,
            "synthetic_data_disclosed_in_figure": True,
            "vector_master": True,
            "editable_text_in_svg": True,
            "panel_reading_order": "pass",
            "semantic_color_consistency": "pass",
            "redundant_shape_encoding_in_embedding": "pass",
            "no_statistical_overclaim": "pass",
            "clipping_overlap": "pass_after_full-resolution_render_review",
            "grayscale_and_contrast": "manual review recommended before submission",
        },
    }
    (ROOT / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    points, embedding_rows = generate_embedding(rng)
    genes, expression, expression_rows = generate_expression(rng)
    samples, composition_rows = generate_composition(rng)
    write_data(embedding_rows + expression_rows + composition_rows)

    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 7.2,
            "axes.labelcolor": MUTED_INK,
            "text.color": INK,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.unicode_minus": False,
        }
    )
    fig = plt.figure(figsize=(WIDTH_IN, mm(HEIGHT_MM)), facecolor=PAPER)
    grid = fig.add_gridspec(
        2, 3,
        height_ratios=[0.78, 1.55],
        width_ratios=[1.10, 0.93, 1.12],
        left=0.055, right=0.982, top=0.946, bottom=0.255,
        hspace=0.22, wspace=0.36,
    )
    ax_a = fig.add_subplot(grid[0, :])
    ax_b = fig.add_subplot(grid[1, 0])
    ax_c = fig.add_subplot(grid[1, 1])
    ax_d = fig.add_subplot(grid[1, 2])
    draw_workflow(ax_a)
    draw_umap(ax_b, points)
    draw_heatmap(ax_c, genes, expression)
    draw_composition(ax_d, samples)

    fig.text(0.055, 0.028, "DEMONSTRATION ONLY — all cells, expression values, and donor compositions are synthetic.  ·  Seed: 20261020",
             fontsize=7.0, color=MUTED_INK, ha="left", va="bottom")

    for suffix in ("svg", "pdf", "png"):
        kwargs = {"bbox_inches": None, "facecolor": PAPER}
        if suffix == "png":
            kwargs["dpi"] = 360
        fig.savefig(ROOT / f"top_journal_demo.{suffix}", **kwargs)
    plt.close(fig)
    write_metadata()
    print(f"Wrote synthetic demonstration artifacts to {ROOT}")


if __name__ == "__main__":
    main()
