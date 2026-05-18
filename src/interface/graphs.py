"""LicenseWise – Graph Module (adapted for current knowledge base)"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
import networkx as nx

# Colour palette
TYPE_COLORS = {
    "permissive": "#4CAF50",
    "weak_copyleft": "#FFC107",
    "copyleft": "#FF7043",
    "other": "#7986CB",
    "proprietary": "#EF5350",
}
DEFAULT_COLOR = "#90A4AE"


# ----------------------------------------------------------------------
# Compatibility matrix – dynamic from license conditions
# ----------------------------------------------------------------------
def _is_compatible(a: dict, b: dict) -> float:
    """
    Returns:
        1.0 = compatible (both allow mixing)
        0.5 = partial / depends (e.g., weak copyleft with strong)
        0.0 = incompatible
    """
    # If either is proprietary, treat as incompatible unless both permissive?
    if a.get("type") == "proprietary" or b.get("type") == "proprietary":
        return 0.0

    # Permissive with anything is compatible
    if a.get("type") == "permissive" or b.get("type") == "permissive":
        return 1.0

    # Copyleft (strong) with weak copyleft: can be partial (LGPL can link to GPL)
    if "copyleft" in a.get("type", "") and "weak_copyleft" in b.get("type", ""):
        return 0.5
    if "weak_copyleft" in a.get("type", "") and "copyleft" in b.get("type", ""):
        return 0.5

    # Strong copyleft with strong: check same_license condition
    if a.get("type") == "copyleft" and b.get("type") == "copyleft":
        if a.get("conditions", {}).get("same_license") and b.get("conditions", {}).get(
            "same_license"
        ):
            # Both require same license – only compatible if identical
            a_id = a.get("spdx_id") or a.get("id")
            b_id = b.get("spdx_id") or b.get("id")
            return 1.0 if a_id == b_id else 0.0
        return 0.5  # one may be more permissive

    # Default to partial
    return 0.5


def make_compatibility_matrix(
    licenses: list[dict], max_licenses: int = 20
) -> plt.Figure:
    """Heatmap with fallback for small license sets."""
    if not licenses:
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("#1E1E2E")
        ax.set_facecolor("#1E1E2E")
        ax.text(
            0.5,
            0.5,
            "No licenses loaded",
            ha="center",
            va="center",
            color="white",
            fontsize=12,
        )
        ax.axis("off")
        return fig

    def _rank(l):
        return l.get("metadata", {}).get("popularity_rank") or 999

    subset = sorted(licenses, key=_rank)[:max_licenses]
    n = len(subset)
    if n < 2:
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("#1E1E2E")
        ax.set_facecolor("#1E1E2E")
        ax.text(
            0.5,
            0.5,
            f"Need at least 2 licenses to build a matrix (found {n})",
            ha="center",
            va="center",
            color="white",
            fontsize=12,
        )
        ax.axis("off")
        return fig

    labels = [l.get("spdx_id") or l.get("id") for l in subset]
    matrix = np.zeros((n, n))
    for i, a in enumerate(subset):
        for j, b in enumerate(subset):
            matrix[i, j] = _is_compatible(a, b)

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "compat", ["#EF5350", "#FFC107", "#4CAF50"]
    )
    fig, ax = plt.subplots(figsize=(max(10, n * 0.55), max(8, n * 0.5)))
    fig.patch.set_facecolor("#1E1E2E")
    ax.set_facecolor("#1E1E2E")

    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8, color="white")
    ax.set_yticklabels(labels, fontsize=8, color="white")

    for i in range(n):
        for j in range(n):
            v = matrix[i, j]
            symbol = "✓" if v == 1.0 else ("~" if v == 0.5 else "✗")
            color = "white" if v < 0.75 else "#1a1a1a"
            ax.text(
                j,
                i,
                symbol,
                ha="center",
                va="center",
                fontsize=7,
                color=color,
                fontweight="bold",
            )

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels(["Incompatible", "Partial", "Compatible"])
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

    ax.set_title(
        "License Compatibility Matrix",
        fontsize=14,
        fontweight="bold",
        color="white",
        pad=12,
    )
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444")
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# Knowledge graph (unchanged, works with current license types)
# ----------------------------------------------------------------------
def make_dependency_graph(licenses: list[dict]) -> plt.Figure:
    """Radial graph: License Type → Conditions → Outcomes."""
    try:
        import networkx as nx
    except ImportError:
        return _missing_dep_figure("networkx")

    G = nx.DiGraph()
    type_nodes = list(TYPE_COLORS.keys())
    condition_nodes = [
        "include_copyright",
        "document_changes",
        "disclose_source",
        "same_license",
        "net_copyleft",
    ]
    outcome_nodes = [
        "Can keep\nmodifications\nprivate",
        "Can use in\nproprietary\nproducts",
        "Can offer\nas SaaS",
        "Derivatives\nmust stay\nopen",
        "Full stack\ndisclosure\nrequired",
        "Patent\nprotection\ngranted",
    ]

    for t in type_nodes:
        G.add_node(t, layer=0)
    for c in condition_nodes:
        G.add_node(c, layer=1)
    for o in outcome_nodes:
        G.add_node(o, layer=2)

    # Type → Condition edges
    type_condition_map = {
        "permissive": ["include_copyright"],
        "weak_copyleft": ["include_copyright", "document_changes", "disclose_source"],
        "copyleft": [
            "include_copyright",
            "document_changes",
            "disclose_source",
            "same_license",
        ],
        "other": ["include_copyright", "same_license"],
        "proprietary": ["include_copyright"],
    }
    for t, conds in type_condition_map.items():
        for c in conds:
            G.add_edge(t, c)

    # Condition → Outcome edges (simplified)
    G.add_edge("disclose_source", "Derivatives\nmust stay\nopen")
    G.add_edge("same_license", "Derivatives\nmust stay\nopen")
    G.add_edge("net_copyleft", "Full stack\ndisclosure\nrequired")
    G.add_edge("net_copyleft", "Can offer\nas SaaS")
    G.add_edge("permissive", "Can keep\nmodifications\nprivate")
    G.add_edge("permissive", "Can use in\nproprietary\nproducts")
    G.add_edge("permissive", "Can offer\nas SaaS")
    G.add_edge("weak_copyleft", "Can use in\nproprietary\nproducts")
    G.add_edge("copyleft", "Derivatives\nmust stay\nopen")
    G.add_edge("proprietary", "Patent\nprotection\ngranted")

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("#1E1E2E")
    ax.set_facecolor("#1E1E2E")
    ax.axis("off")

    # Manual layered positions
    def _layer_positions(nodes, x, y_start, y_step):
        return {n: (x, y_start - i * y_step) for i, n in enumerate(nodes)}

    pos = {}
    pos.update(_layer_positions(type_nodes, 0.0, 1.8, 0.9))
    pos.update(_layer_positions(condition_nodes, 0.45, 1.8, 0.9))
    pos.update(_layer_positions(outcome_nodes, 0.9, 2.2, 0.75))

    # Draw edges
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        ax.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops=dict(arrowstyle="-|>", color="#555577", lw=1.2),
        )

    # Draw type nodes
    for t in type_nodes:
        x, y = pos[t]
        color = TYPE_COLORS.get(t, DEFAULT_COLOR)
        ax.scatter(
            x, y, s=1800, color=color, zorder=5, edgecolors="white", linewidths=1.5
        )
        ax.text(
            x,
            y,
            t.replace("_", "\n"),
            ha="center",
            va="center",
            fontsize=7.5,
            fontweight="bold",
            color="white",
            zorder=6,
        )

    # Draw condition nodes
    for c in condition_nodes:
        x, y = pos[c]
        ax.scatter(
            x,
            y,
            s=1200,
            color="#37474F",
            zorder=5,
            edgecolors="#78909C",
            linewidths=1.2,
            marker="D",
        )
        ax.text(
            x,
            y,
            c.replace("_", "\n"),
            ha="center",
            va="center",
            fontsize=6.5,
            color="#B0BEC5",
            zorder=6,
        )

    # Draw outcome nodes
    for o in outcome_nodes:
        if o in pos:
            x, y = pos[o]
            ax.scatter(
                x,
                y,
                s=1500,
                color="#263238",
                zorder=5,
                edgecolors="#546E7A",
                linewidths=1.2,
                marker="s",
            )
            ax.text(
                x,
                y,
                o,
                ha="center",
                va="center",
                fontsize=6.5,
                color="#CFD8DC",
                zorder=6,
            )

    # Legend
    legend_patches = [mpatches.Patch(color=c, label=t) for t, c in TYPE_COLORS.items()]
    legend_patches += [
        mpatches.Patch(color="#37474F", label="Condition (◆)"),
        mpatches.Patch(color="#263238", label="Outcome (■)"),
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower right",
        facecolor="#2D2D3F",
        edgecolor="#555",
        labelcolor="white",
        fontsize=8,
        framealpha=0.9,
    )

    for label, x in [("License Types", 0.0), ("Conditions", 0.45), ("Outcomes", 0.9)]:
        ax.text(
            x,
            2.55,
            label,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#90CAF9",
        )

    ax.set_xlim(-0.2, 1.1)
    ax.set_ylim(-0.3, 2.8)
    ax.set_title(
        "License Knowledge Graph — Types → Conditions → Outcomes",
        fontsize=13,
        fontweight="bold",
        color="white",
        pad=10,
    )
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# Statistics charts (2×2 grid)
# ----------------------------------------------------------------------
def make_statistics_charts(licenses: list[dict]) -> plt.Figure:
    """2×2 grid with fallback for missing popularity data."""
    if not licenses:
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor("#1E1E2E")
        ax.text(
            0.5,
            0.5,
            "No licenses loaded",
            ha="center",
            va="center",
            color="white",
            fontsize=12,
        )
        ax.axis("off")
        return fig

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.patch.set_facecolor("#1E1E2E")
    for ax in axes.flat:
        ax.set_facecolor("#1E1E2E")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")

    # ---- Type distribution donut ----
    ax = axes[0, 0]
    type_counts = {}
    for l in licenses:
        t = l.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    labels = list(type_counts.keys())
    sizes = list(type_counts.values())
    colors = [TYPE_COLORS.get(t, DEFAULT_COLOR) for t in labels]
    wedges, _, autotexts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        autopct="%1.0f%%",
        startangle=140,
        wedgeprops=dict(width=0.55, edgecolor="#1E1E2E", linewidth=2),
    )
    for at in autotexts:
        at.set(color="white", fontsize=8, fontweight="bold")
    ax.legend(
        wedges,
        [f"{l} ({c})" for l, c in zip(labels, sizes)],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.18),
        facecolor="#2D2D3F",
        edgecolor="#555",
        labelcolor="white",
        fontsize=8,
        ncol=2,
    )
    ax.set_title(
        "License Type Distribution",
        color="white",
        fontsize=11,
        fontweight="bold",
        pad=8,
    )

    # # ---- Popularity bar ----
    # ax = axes[0, 1]
    # ranked = sorted([l for l in licenses if l.get("metadata", {}).get("popularity_rank")],
    #                 key=lambda l: l["metadata"]["popularity_rank"])[:15]
    # names = [l.get("spdx_id") or l.get("id") for l in ranked]
    # ranks = [l["metadata"]["popularity_rank"] for l in ranked]
    # colors_bar = [TYPE_COLORS.get(l.get("type", ""), DEFAULT_COLOR) for l in ranked]
    # max_r = max(ranks)
    # widths = [max_r - r + 1 for r in ranks]
    # ax.barh(names[::-1], widths[::-1], color=colors_bar[::-1], edgecolor="#1E1E2E", linewidth=0.8)
    # ax.set_xlabel("Relative popularity (higher = more popular)", color="white", fontsize=8)
    # ax.set_title("Top 15 Licenses by Popularity", color="white", fontsize=11, fontweight="bold")
    # ax.tick_params(axis="y", labelsize=8, labelcolor="white")
    # ax.tick_params(axis="x", labelcolor="white")
    # ax.set_xlim(0, max_r + 1)
    # for bar, rank in zip(ax.containers[0][::-1], ranks):
    #     ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f"#{rank}", va="center", fontsize=7, color="#90CAF9")

    # ---- OSI/FSF approval ----
    ax = axes[1, 0]
    categories = list(TYPE_COLORS.keys())
    osi_yes, osi_no, fsf_yes, fsf_no = [], [], [], []
    for cat in categories:
        group = [l for l in licenses if l.get("type") == cat]
        osi_yes.append(
            sum(1 for l in group if l.get("metadata", {}).get("osi_approved"))
        )
        osi_no.append(
            sum(1 for l in group if not l.get("metadata", {}).get("osi_approved"))
        )
        fsf_yes.append(sum(1 for l in group if l.get("metadata", {}).get("fsf_free")))
        fsf_no.append(
            sum(1 for l in group if not l.get("metadata", {}).get("fsf_free"))
        )
    x = np.arange(len(categories))
    width = 0.2
    ax.bar(
        x - 1.5 * width,
        osi_yes,
        width,
        label="OSI ✅",
        color="#4CAF50",
        edgecolor="#1E1E2E",
    )
    ax.bar(
        x - 0.5 * width,
        osi_no,
        width,
        label="OSI ❌",
        color="#EF5350",
        edgecolor="#1E1E2E",
    )
    ax.bar(
        x + 0.5 * width,
        fsf_yes,
        width,
        label="FSF ✅",
        color="#42A5F5",
        edgecolor="#1E1E2E",
    )
    ax.bar(
        x + 1.5 * width,
        fsf_no,
        width,
        label="FSF ❌",
        color="#FF7043",
        edgecolor="#1E1E2E",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(
        [c.replace("_", "\n") for c in categories], fontsize=8, color="white"
    )
    ax.set_ylabel("Count", color="white", fontsize=9)
    ax.set_title(
        "OSI & FSF Approval by License Type",
        color="white",
        fontsize=11,
        fontweight="bold",
    )
    ax.legend(facecolor="#2D2D3F", edgecolor="#555", labelcolor="white", fontsize=8)

    # ---- Permission coverage ----
    ax = axes[1, 1]
    permission_keys = ["commercial_use", "distribution", "modification", "private_use"]
    perm_labels = ["Commercial", "Distribution", "Modification", "Private use"]
    perm_colors = ["#66BB6A", "#42A5F5", "#FFA726", "#AB47BC"]
    type_perm_counts = {cat: [0] * 4 for cat in categories}
    type_totals = {cat: 0 for cat in categories}
    for l in licenses:
        cat = l.get("type", "")
        if cat not in type_perm_counts:
            continue
        type_totals[cat] += 1
        for i, pk in enumerate(permission_keys):
            if l.get("permissions", {}).get(pk):
                type_perm_counts[cat][i] += 1
    x = np.arange(len(categories))
    bottom = np.zeros(len(categories))
    for i, (pl, pc) in enumerate(zip(perm_labels, perm_colors)):
        heights = [
            (type_perm_counts[cat][i] / type_totals[cat] * 100)
            if type_totals[cat]
            else 0
            for cat in categories
        ]
        ax.bar(
            x,
            heights,
            width=0.55,
            bottom=bottom,
            label=pl,
            color=pc,
            edgecolor="#1E1E2E",
            linewidth=0.8,
        )
        bottom += np.array(heights)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [c.replace("_", "\n") for c in categories], fontsize=8, color="white"
    )
    ax.set_ylabel("% of licenses granting permission", color="white", fontsize=9)
    ax.set_title(
        "Permission Coverage per License Type",
        color="white",
        fontsize=11,
        fontweight="bold",
    )
    ax.set_ylim(0, 420)
    ax.legend(
        facecolor="#2D2D3F",
        edgecolor="#555",
        labelcolor="white",
        fontsize=8,
        loc="upper right",
    )

    fig.suptitle(
        "LicenseWise – Knowledge Base Statistics",
        fontsize=14,
        fontweight="bold",
        color="white",
        y=1.01,
    )
    fig.tight_layout()
    return fig


def _missing_dep_figure(package: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor("#1E1E2E")
    ax.set_facecolor("#1E1E2E")
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        f"Missing dependency: {package}\nInstall with: pip install {package}",
        ha="center",
        va="center",
        fontsize=12,
        color="#EF5350",
        transform=ax.transAxes,
    )
    return fig
