"""LicenseWise – Graph Module (adapted for current knowledge base)"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
import networkx as nx

from interface.graph_theme import (
    TYPE_COLORS,
    DEFAULT_COLOR,
    BG_COLOR,
    GRID_COLOR,
    EDGE_COLOR,
    LEGEND_FACE,
    LEGEND_EDGE,
    TEXT_COLOR,
    ACCENT_COLOR,
    FONT_TITLE,
    FONT_LABEL,
    FONT_TICK,
    FONT_NODE_LARGE,
    FONT_NODE_SMALL,
    NODE_SIZE_TYPE,
    NODE_SIZE_CONDITION,
    NODE_SIZE_OUTCOME,
    MARKER_CONDITION,
    MARKER_OUTCOME,
    COLOR_CONDITION,
    COLOR_CONDITION_EDGE,
    COLOR_OUTCOME,
    COLOR_OUTCOME_EDGE,
    TEXT_CONDITION,
    TEXT_OUTCOME,
    CONDITION_NODES,
    OUTCOME_NODES,
    TYPE_CONDITION_MAP,
    CONDITION_OUTCOME_EDGES,
    LAYER_HEADERS,
    LAYER_X_TYPE,
    LAYER_X_CONDITION,
    LAYER_X_OUTCOME,
    LAYER_Y_START_TYPE,
    LAYER_Y_STEP_TYPE,
    LAYER_Y_START_CONDITION,
    LAYER_Y_STEP_CONDITION,
    LAYER_Y_START_OUTCOME,
    LAYER_Y_STEP_OUTCOME,
    COMPAT_CMAP_COLORS,
)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _empty_figure(message: str, figsize: tuple = (6, 4)) -> plt.Figure:
    """Create a themed empty figure with a centered message."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.text(
        0.5, 0.5, message,
        ha="center", va="center", color=TEXT_COLOR, fontsize=12,
    )
    ax.axis("off")
    return fig


def _apply_ax_theme(ax: plt.Axes) -> None:
    """Apply dark theme to an axes."""
    ax.set_facecolor(BG_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)


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
    if a.get("type") == "proprietary" or b.get("type") == "proprietary":
        return 0.0

    if a.get("type") == "permissive" or b.get("type") == "permissive":
        return 1.0

    if "copyleft" in a.get("type", "") and "weak_copyleft" in b.get("type", ""):
        return 0.5
    if "weak_copyleft" in a.get("type", "") and "copyleft" in b.get("type", ""):
        return 0.5

    if a.get("type") == "copyleft" and b.get("type") == "copyleft":
        if a.get("conditions", {}).get("same_license") and b.get("conditions", {}).get(
            "same_license"
        ):
            a_id = a.get("spdx_id") or a.get("id")
            b_id = b.get("spdx_id") or b.get("id")
            return 1.0 if a_id == b_id else 0.0
        return 0.5

    return 0.5


def make_compatibility_matrix(
    licenses: list[dict], max_licenses: int = 20
) -> plt.Figure:
    """Heatmap with fallback for small license sets."""
    if not licenses:
        return _empty_figure("No licenses loaded")

    def _rank(l):
        return l.get("metadata", {}).get("popularity_rank") or 999

    subset = sorted(licenses, key=_rank)[:max_licenses]
    n = len(subset)
    if n < 2:
        return _empty_figure(f"Need at least 2 licenses to build a matrix (found {n})")

    labels = [l.get("spdx_id") or l.get("id") for l in subset]
    matrix = np.zeros((n, n))
    for i, a in enumerate(subset):
        for j, b in enumerate(subset):
            matrix[i, j] = _is_compatible(a, b)

    cmap = mcolors.LinearSegmentedColormap.from_list("compat", COMPAT_CMAP_COLORS)
    fig, ax = plt.subplots(figsize=(max(10, n * 0.55), max(8, n * 0.5)))
    fig.patch.set_facecolor(BG_COLOR)
    _apply_ax_theme(ax)

    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=FONT_TICK, color=TEXT_COLOR)
    ax.set_yticklabels(labels, fontsize=FONT_TICK, color=TEXT_COLOR)

    for i in range(n):
        for j in range(n):
            v = matrix[i, j]
            symbol = "\u2713" if v == 1.0 else ("~" if v == 0.5 else "\u2717")
            color = TEXT_COLOR if v < 0.75 else "#1a1a1a"
            ax.text(
                j, i, symbol,
                ha="center", va="center", fontsize=7,
                color=color, fontweight="bold",
            )

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels(["Incompatible", "Partial", "Compatible"])
    cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COLOR)

    ax.set_title(
        "License Compatibility Matrix",
        fontsize=FONT_TITLE, fontweight="bold", color=TEXT_COLOR, pad=12,
    )
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# Knowledge graph
# ----------------------------------------------------------------------
def make_dependency_graph(licenses: list[dict]) -> plt.Figure:
    """Radial graph: License Type → Conditions → Outcomes."""
    try:
        import networkx as nx
    except ImportError:
        return _missing_dep_figure("networkx")

    G = nx.DiGraph()
    type_nodes = list(TYPE_COLORS.keys())

    for t in type_nodes:
        G.add_node(t, layer=0)
    for c in CONDITION_NODES:
        G.add_node(c, layer=1)
    for o in OUTCOME_NODES:
        G.add_node(o, layer=2)

    for t, conds in TYPE_CONDITION_MAP.items():
        for c in conds:
            G.add_edge(t, c)

    for src, dst in CONDITION_OUTCOME_EDGES:
        G.add_edge(src, dst)

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")

    def _layer_positions(nodes, x, y_start, y_step):
        return {n: (x, y_start - i * y_step) for i, n in enumerate(nodes)}

    pos = {}
    pos.update(_layer_positions(type_nodes, LAYER_X_TYPE, LAYER_Y_START_TYPE, LAYER_Y_STEP_TYPE))
    pos.update(_layer_positions(CONDITION_NODES, LAYER_X_CONDITION, LAYER_Y_START_CONDITION, LAYER_Y_STEP_CONDITION))
    pos.update(_layer_positions(OUTCOME_NODES, LAYER_X_OUTCOME, LAYER_Y_START_OUTCOME, LAYER_Y_STEP_OUTCOME))

    # Draw edges
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR, lw=1.2),
        )

    # Draw type nodes
    for t in type_nodes:
        x, y = pos[t]
        color = TYPE_COLORS.get(t, DEFAULT_COLOR)
        ax.scatter(x, y, s=NODE_SIZE_TYPE, color=color, zorder=5, edgecolors=TEXT_COLOR, linewidths=1.5)
        ax.text(
            x, y, t.replace("_", "\n"),
            ha="center", va="center", fontsize=FONT_NODE_LARGE,
            fontweight="bold", color=TEXT_COLOR, zorder=6,
        )

    # Draw condition nodes
    for c in CONDITION_NODES:
        x, y = pos[c]
        ax.scatter(
            x, y, s=NODE_SIZE_CONDITION, color=COLOR_CONDITION,
            zorder=5, edgecolors=COLOR_CONDITION_EDGE, linewidths=1.2,
            marker=MARKER_CONDITION,
        )
        ax.text(
            x, y, c.replace("_", "\n"),
            ha="center", va="center", fontsize=FONT_NODE_SMALL,
            color=TEXT_CONDITION, zorder=6,
        )

    # Draw outcome nodes
    for o in OUTCOME_NODES:
        if o in pos:
            x, y = pos[o]
            ax.scatter(
                x, y, s=NODE_SIZE_OUTCOME, color=COLOR_OUTCOME,
                zorder=5, edgecolors=COLOR_OUTCOME_EDGE, linewidths=1.2,
                marker=MARKER_OUTCOME,
            )
            ax.text(
                x, y, o,
                ha="center", va="center", fontsize=FONT_NODE_SMALL,
                color=TEXT_OUTCOME, zorder=6,
            )

    # Legend
    legend_patches = [mpatches.Patch(color=c, label=t) for t, c in TYPE_COLORS.items()]
    legend_patches += [
        mpatches.Patch(color=COLOR_CONDITION, label="Condition (\u25c6)"),
        mpatches.Patch(color=COLOR_OUTCOME, label="Outcome (\u25a0)"),
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower right",
        facecolor=LEGEND_FACE, edgecolor=LEGEND_EDGE,
        labelcolor=TEXT_COLOR, fontsize=8, framealpha=0.9,
    )

    for label, x in LAYER_HEADERS:
        ax.text(
            x, 2.55, label,
            ha="center", va="center", fontsize=FONT_LABEL,
            fontweight="bold", color=ACCENT_COLOR,
        )

    ax.set_xlim(-0.2, 1.1)
    ax.set_ylim(-0.3, 2.8)
    ax.set_title(
        "License Knowledge Graph \u2014 Types \u2192 Conditions \u2192 Outcomes",
        fontsize=13, fontweight="bold", color=TEXT_COLOR, pad=10,
    )
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# Statistics charts (2×2 grid)
# ----------------------------------------------------------------------
def make_statistics_charts(licenses: list[dict]) -> plt.Figure:
    """2×2 grid with fallback for missing popularity data."""
    if not licenses:
        return _empty_figure("No licenses loaded", figsize=(8, 6))

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.patch.set_facecolor(BG_COLOR)
    for ax in axes.flat:
        _apply_ax_theme(ax)

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
        sizes, labels=None, colors=colors, autopct="%1.0f%%",
        startangle=140,
        wedgeprops=dict(width=0.55, edgecolor=BG_COLOR, linewidth=2),
    )
    for at in autotexts:
        at.set(color=TEXT_COLOR, fontsize=8, fontweight="bold")
    ax.legend(
        wedges, [f"{l} ({c})" for l, c in zip(labels, sizes)],
        loc="lower center", bbox_to_anchor=(0.5, -0.18),
        facecolor=LEGEND_FACE, edgecolor=LEGEND_EDGE,
        labelcolor=TEXT_COLOR, fontsize=8, ncol=2,
    )
    ax.set_title(
        "License Type Distribution",
        color=TEXT_COLOR, fontsize=11, fontweight="bold", pad=8,
    )

    # ---- OSI/FSF approval ----
    ax = axes[1, 0]
    categories = list(TYPE_COLORS.keys())
    osi_yes, osi_no, fsf_yes, fsf_no = [], [], [], []
    for cat in categories:
        group = [l for l in licenses if l.get("type") == cat]
        osi_yes.append(sum(1 for l in group if l.get("metadata", {}).get("osi_approved")))
        osi_no.append(sum(1 for l in group if not l.get("metadata", {}).get("osi_approved")))
        fsf_yes.append(sum(1 for l in group if l.get("metadata", {}).get("fsf_free")))
        fsf_no.append(sum(1 for l in group if not l.get("metadata", {}).get("fsf_free")))
    x = np.arange(len(categories))
    width = 0.2
    ax.bar(x - 1.5 * width, osi_yes, width, label="OSI \u2705", color="#4CAF50", edgecolor=BG_COLOR)
    ax.bar(x - 0.5 * width, osi_no, width, label="OSI \u274c", color="#EF5350", edgecolor=BG_COLOR)
    ax.bar(x + 0.5 * width, fsf_yes, width, label="FSF \u2705", color="#42A5F5", edgecolor=BG_COLOR)
    ax.bar(x + 1.5 * width, fsf_no, width, label="FSF \u274c", color="#FF7043", edgecolor=BG_COLOR)
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", "\n") for c in categories], fontsize=FONT_TICK, color=TEXT_COLOR)
    ax.set_ylabel("Count", color=TEXT_COLOR, fontsize=FONT_LABEL)
    ax.set_title(
        "OSI & FSF Approval by License Type",
        color=TEXT_COLOR, fontsize=11, fontweight="bold",
    )
    ax.legend(facecolor=LEGEND_FACE, edgecolor=LEGEND_EDGE, labelcolor=TEXT_COLOR, fontsize=8)

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
            if type_totals[cat] else 0
            for cat in categories
        ]
        ax.bar(
            x, heights, width=0.55, bottom=bottom,
            label=pl, color=pc, edgecolor=BG_COLOR, linewidth=0.8,
        )
        bottom += np.array(heights)
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", "\n") for c in categories], fontsize=FONT_TICK, color=TEXT_COLOR)
    ax.set_ylabel("% of licenses granting permission", color=TEXT_COLOR, fontsize=FONT_LABEL)
    ax.set_title(
        "Permission Coverage per License Type",
        color=TEXT_COLOR, fontsize=11, fontweight="bold",
    )
    ax.set_ylim(0, 420)
    ax.legend(facecolor=LEGEND_FACE, edgecolor=LEGEND_EDGE, labelcolor=TEXT_COLOR, fontsize=8, loc="upper right")

    fig.suptitle(
        "LicenseWise \u2013 Knowledge Base Statistics",
        fontsize=FONT_TITLE, fontweight="bold", color=TEXT_COLOR, y=1.01,
    )
    fig.tight_layout()
    return fig


def _missing_dep_figure(package: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    ax.text(
        0.5, 0.5,
        f"Missing dependency: {package}\nInstall with: pip install {package}",
        ha="center", va="center", fontsize=12,
        color="#EF5350", transform=ax.transAxes,
    )
    return fig
