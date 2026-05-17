"""
LicenseWise – Graph Module
interface/graphs.py

Provides three figure factories, each returning a matplotlib Figure
that can be embedded in Gradio or saved to disk independently.

Public API
----------
    make_compatibility_matrix(licenses)  → Figure
    make_dependency_graph(licenses)      → Figure
    make_statistics_charts(licenses)     → Figure

Usage (standalone)
------------------
    from interface.graphs import make_compatibility_matrix, make_dependency_graph, make_statistics_charts
    import json, matplotlib.pyplot as plt

    with open("_Licenses/licenses.json") as f:
        db = json.load(f)
    licenses = db["licenses"] if isinstance(db, dict) else db

    fig = make_compatibility_matrix(licenses)
    plt.show()

Usage (Gradio tab)
------------------
    See build_graphs_tab() at the bottom of this file,
    which is imported and called by gradio_app.py.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")                        # non-interactive backend for Gradio
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np

# ---------------------------------------------------------------------------
# Colour palette (consistent across all charts)
# ---------------------------------------------------------------------------

TYPE_COLORS = {
    "permissive":    "#4CAF50",   # green
    "weak_copyleft": "#FFC107",   # amber
    "copyleft":      "#FF7043",   # deep orange
    "other":         "#7986CB",   # indigo (Creative Commons)
    "proprietary":   "#EF5350",   # red
}
DEFAULT_COLOR = "#90A4AE"

# ---------------------------------------------------------------------------
# Compatibility rules
# Encoded as (type_a, type_b) → compatible (True/False/None=partial)
# None means "depends on direction / use-case"
# ---------------------------------------------------------------------------

_COMPAT: dict[tuple[str, str], bool | None] = {
    # permissive + anything → generally fine
    ("permissive", "permissive"):    True,
    ("permissive", "weak_copyleft"): True,
    ("permissive", "copyleft"):      True,
    ("permissive", "other"):         True,
    ("permissive", "proprietary"):   True,

    # weak_copyleft
    ("weak_copyleft", "permissive"):    True,
    ("weak_copyleft", "weak_copyleft"): None,   # depends on specific licenses
    ("weak_copyleft", "copyleft"):      None,
    ("weak_copyleft", "other"):         None,
    ("weak_copyleft", "proprietary"):   False,

    # copyleft
    ("copyleft", "permissive"):    True,         # permissive code INTO GPL project is fine
    ("copyleft", "weak_copyleft"): None,
    ("copyleft", "copyleft"):      None,         # GPL-2 vs GPL-3 incompatibility
    ("copyleft", "other"):         False,
    ("copyleft", "proprietary"):   False,

    # other (CC)
    ("other", "permissive"):    True,
    ("other", "weak_copyleft"): None,
    ("other", "copyleft"):      False,
    ("other", "other"):         None,
    ("other", "proprietary"):   False,

    # proprietary
    ("proprietary", "permissive"):    True,
    ("proprietary", "weak_copyleft"): False,
    ("proprietary", "copyleft"):      False,
    ("proprietary", "other"):         False,
    ("proprietary", "proprietary"):   None,
}

# Finer-grained SPDX-level overrides (src → dst → compatible)
_SPDX_OVERRIDES: dict[str, dict[str, bool | None]] = {
    "GPL-2.0-only": {
        "GPL-3.0-only":    False,   # GPL-2.0 only ≠ GPL-3.0
        "Apache-2.0":      False,   # patent clause incompatibility
        "AGPL-3.0-only":   False,
    },
    "GPL-3.0-only": {
        "Apache-2.0":      False,   # GPL-3.0 is incompatible with Apache-2.0 at distribution
        "LGPL-2.1-only":   None,
        "AGPL-3.0-only":   True,    # GPL-3 code can go into AGPL-3
    },
    "AGPL-3.0-only": {
        "GPL-3.0-only":    False,   # AGPL → GPL requires stripping network clause
    },
    "LGPL-2.1-only": {
        "GPL-2.0-only":    True,
        "GPL-3.0-only":    None,
    },
    "MPL-2.0": {
        "GPL-2.0-only":    True,
        "GPL-3.0-only":    True,
        "Apache-2.0":      True,
    },
    "Apache-2.0": {
        "GPL-2.0-only":    False,
        "GPL-3.0-only":    False,
        "MIT":             True,
        "BSD-2-Clause":    True,
        "BSD-3-Clause":    True,
    },
    "CDDL-1.0": {
        "GPL-2.0-only":    False,
        "GPL-3.0-only":    False,
    },
}


def _compat_value(a: dict, b: dict) -> float:
    """
    Return a numeric value for heatmap:
      1.0 = compatible
      0.5 = partial / depends
      0.0 = incompatible
    """
    sid_a = a.get("spdx_id") or a.get("id")
    sid_b = b.get("spdx_id") or b.get("id")

    # SPDX override first
    override = _SPDX_OVERRIDES.get(sid_a, {}).get(sid_b)
    if override is None and sid_a != sid_b:
        override = _SPDX_OVERRIDES.get(sid_b, {}).get(sid_a)

    if override is True:  return 1.0
    if override is False: return 0.0
    if override is None and (sid_a in _SPDX_OVERRIDES or sid_b in _SPDX_OVERRIDES):
        return 0.5

    # Fall back to type-level rules
    ta, tb = a.get("type", ""), b.get("type", "")
    result = _COMPAT.get((ta, tb))
    if result is True:  return 1.0
    if result is False: return 0.0
    return 0.5   # None → partial


# ---------------------------------------------------------------------------
# 1. Compatibility Matrix
# ---------------------------------------------------------------------------

def make_compatibility_matrix(
    licenses: list[dict],
    max_licenses: int = 20,
) -> plt.Figure:
    """
    Heatmap showing pairwise license compatibility.
    Green = compatible, Yellow = partial/depends, Red = incompatible.
    """
    # Prefer popular licenses when the list is large
    def _rank(l):
        return l.get("metadata", {}).get("popularity_rank") or 999

    subset = sorted(licenses, key=_rank)[:max_licenses]
    labels = [l.get("spdx_id") or l.get("id") for l in subset]
    n = len(subset)

    matrix = np.zeros((n, n))
    for i, a in enumerate(subset):
        for j, b in enumerate(subset):
            matrix[i, j] = _compat_value(a, b)

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

    # Annotate cells
    for i in range(n):
        for j in range(n):
            v = matrix[i, j]
            symbol = "✓" if v == 1.0 else ("~" if v == 0.5 else "✗")
            color  = "white" if v < 0.75 else "#1a1a1a"
            ax.text(j, i, symbol, ha="center", va="center",
                    fontsize=7, color=color, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels(["Incompatible", "Partial", "Compatible"])
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

    ax.set_title("License Compatibility Matrix", fontsize=14,
                 fontweight="bold", color="white", pad=12)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444")

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 2. Dependency / Knowledge Graph
# ---------------------------------------------------------------------------

def make_dependency_graph(licenses: list[dict]) -> plt.Figure:
    """
    Radial graph:  License Type (hub) → Condition nodes → Outcome nodes.
    Shows how type drives conditions which drive practical outcomes.
    """
    try:
        import networkx as nx
    except ImportError:
        return _missing_dep_figure("networkx")

    G = nx.DiGraph()

    # --- Define the conceptual graph ---
    type_nodes = list(TYPE_COLORS.keys())

    # Condition nodes (shared)
    condition_nodes = [
        "include_copyright", "document_changes",
        "disclose_source", "same_license", "net_copyleft",
    ]

    # Outcome nodes
    outcome_nodes = [
        "Can keep\nmodifications\nprivate",
        "Can use in\nproprietary\nproducts",
        "Can offer\nas SaaS",
        "Derivatives\nmust stay\nopen",
        "Full stack\ndisclosure\nrequired",
        "Patent\nprotection\ngranted",
    ]

    for t in type_nodes:      G.add_node(t,           layer=0)
    for c in condition_nodes: G.add_node(c,           layer=1)
    for o in outcome_nodes:   G.add_node(o,           layer=2)

    # Type → Condition edges (which conditions each type typically triggers)
    type_condition_map = {
        "permissive":    ["include_copyright"],
        "weak_copyleft": ["include_copyright", "document_changes", "disclose_source"],
        "copyleft":      ["include_copyright", "document_changes", "disclose_source", "same_license"],
        "other":         ["include_copyright", "same_license"],
        "proprietary":   ["include_copyright"],
    }
    for t, conds in type_condition_map.items():
        for c in conds:
            G.add_edge(t, c)

    # Condition → Outcome edges
    cond_outcome_map = {
        "include_copyright":  [],
        "document_changes":   [],
        "disclose_source":    ["Derivatives\nmust stay\nopen"],
        "same_license":       ["Derivatives\nmust stay\nopen"],
        "net_copyleft":       ["Full stack\ndisclosure\nrequired", "Can offer\nas SaaS"],
    }
    # Absent conditions → positive outcomes
    G.add_edge("permissive",    "Can keep\nmodifications\nprivate")
    G.add_edge("permissive",    "Can use in\nproprietary\nproducts")
    G.add_edge("permissive",    "Can offer\nas SaaS")
    G.add_edge("weak_copyleft", "Can use in\nproprietary\nproducts")
    G.add_edge("copyleft",      "Derivatives\nmust stay\nopen")
    G.add_edge("proprietary",   "Patent\nprotection\ngranted")
    G.add_edge("disclose_source", "Derivatives\nmust stay\nopen")
    G.add_edge("same_license",    "Derivatives\nmust stay\nopen")
    G.add_edge("net_copyleft",    "Full stack\ndisclosure\nrequired")

    # --- Layout ---
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("#1E1E2E")
    ax.set_facecolor("#1E1E2E")
    ax.axis("off")

    # Manual layered positions
    def _layer_positions(nodes, x, y_start, y_step):
        return {n: (x, y_start - i * y_step) for i, n in enumerate(nodes)}

    pos = {}
    pos.update(_layer_positions(type_nodes,      0.0, 1.8, 0.9))
    pos.update(_layer_positions(condition_nodes,  0.45, 1.8, 0.9))
    pos.update(_layer_positions(outcome_nodes,    0.9,  2.2, 0.75))

    # Draw edges
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(
                arrowstyle="-|>", color="#555577",
                lw=1.2, connectionstyle="arc3,rad=0.05"
            )
        )

    # Draw type nodes
    for t in type_nodes:
        x, y = pos[t]
        color = TYPE_COLORS.get(t, DEFAULT_COLOR)
        ax.scatter(x, y, s=1800, color=color, zorder=5, edgecolors="white", linewidths=1.5)
        ax.text(x, y, t.replace("_", "\n"), ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="white", zorder=6)

    # Draw condition nodes
    for c in condition_nodes:
        x, y = pos[c]
        ax.scatter(x, y, s=1200, color="#37474F", zorder=5,
                   edgecolors="#78909C", linewidths=1.2, marker="D")
        ax.text(x, y, c.replace("_", "\n"), ha="center", va="center",
                fontsize=6.5, color="#B0BEC5", zorder=6)

    # Draw outcome nodes
    for o in outcome_nodes:
        if o in pos:
            x, y = pos[o]
            ax.scatter(x, y, s=1500, color="#263238", zorder=5,
                       edgecolors="#546E7A", linewidths=1.2, marker="s")
            ax.text(x, y, o, ha="center", va="center",
                    fontsize=6.5, color="#CFD8DC", zorder=6)

    # Legend
    legend_patches = [
        mpatches.Patch(color=c, label=t) for t, c in TYPE_COLORS.items()
    ]
    legend_patches += [
        mpatches.Patch(color="#37474F", label="Condition (◆)"),
        mpatches.Patch(color="#263238", label="Outcome (■)"),
    ]
    ax.legend(handles=legend_patches, loc="lower right",
              facecolor="#2D2D3F", edgecolor="#555", labelcolor="white",
              fontsize=8, framealpha=0.9)

    # Column headers
    for label, x in [("License Types", 0.0), ("Conditions", 0.45), ("Outcomes", 0.9)]:
        ax.text(x, 2.55, label, ha="center", va="center",
                fontsize=10, fontweight="bold", color="#90CAF9",
                transform=ax.transData)

    ax.set_xlim(-0.2, 1.1)
    ax.set_ylim(-0.3, 2.8)
    ax.set_title("License Knowledge Graph — Types → Conditions → Outcomes",
                 fontsize=13, fontweight="bold", color="white", pad=10)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 3. Statistics Charts  (2×2 grid)
# ---------------------------------------------------------------------------

def make_statistics_charts(licenses: list[dict]) -> plt.Figure:
    """
    2×2 grid:
      [0,0] Donut – breakdown by license type
      [0,1] Bar   – top 15 licenses by popularity rank
      [1,0] Bar   – OSI approved vs not
      [1,1] Stacked bar – permission coverage per type
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.patch.set_facecolor("#1E1E2E")
    for ax in axes.flat:
        ax.set_facecolor("#1E1E2E")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")

    # ── [0,0] Donut – license type distribution ──────────────────────────
    ax = axes[0, 0]
    type_counts: dict[str, int] = {}
    for l in licenses:
        t = l.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    labels  = list(type_counts.keys())
    sizes   = list(type_counts.values())
    colors  = [TYPE_COLORS.get(t, DEFAULT_COLOR) for t in labels]
    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, colors=colors,
        autopct="%1.0f%%", startangle=140,
        wedgeprops=dict(width=0.55, edgecolor="#1E1E2E", linewidth=2),
        pctdistance=0.75,
    )
    for at in autotexts:
        at.set(color="white", fontsize=8, fontweight="bold")

    legend = ax.legend(
        wedges, [f"{l} ({c})" for l, c in zip(labels, sizes)],
        loc="lower center", bbox_to_anchor=(0.5, -0.18),
        facecolor="#2D2D3F", edgecolor="#555", labelcolor="white",
        fontsize=8, ncol=2,
    )
    ax.set_title("License Type Distribution", color="white",
                 fontsize=11, fontweight="bold", pad=8)

    # ── [0,1] Horizontal bar – popularity ranking ─────────────────────────
    ax = axes[0, 1]
    ranked = sorted(
        [l for l in licenses if l.get("metadata", {}).get("popularity_rank")],
        key=lambda l: l["metadata"]["popularity_rank"]
    )[:15]

    names  = [l.get("spdx_id") or l.get("id") for l in ranked]
    ranks  = [l["metadata"]["popularity_rank"] for l in ranked]
    colors_bar = [TYPE_COLORS.get(l.get("type", ""), DEFAULT_COLOR) for l in ranked]

    # Invert so rank 1 = longest bar
    max_r  = max(ranks)
    widths = [max_r - r + 1 for r in ranks]

    bars = ax.barh(names[::-1], widths[::-1], color=colors_bar[::-1],
                   edgecolor="#1E1E2E", linewidth=0.8)
    ax.set_xlabel("Relative popularity (higher = more popular)", color="white", fontsize=8)
    ax.set_title("Top 15 Licenses by Popularity", color="white",
                 fontsize=11, fontweight="bold")
    ax.tick_params(axis="y", labelsize=8, labelcolor="white")
    ax.tick_params(axis="x", labelcolor="white")
    ax.set_xlim(0, max_r + 1)

    for bar, rank in zip(bars[::-1], ranks):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"#{rank}", va="center", fontsize=7, color="#90CAF9")

    # ── [1,0] Grouped bar – OSI / FSF approval ───────────────────────────
    ax = axes[1, 0]
    categories = list(TYPE_COLORS.keys())
    osi_yes, osi_no, fsf_yes, fsf_no = [], [], [], []

    for cat in categories:
        group = [l for l in licenses if l.get("type") == cat]
        osi_yes.append(sum(1 for l in group if l.get("metadata", {}).get("osi_approved")))
        osi_no.append( sum(1 for l in group if not l.get("metadata", {}).get("osi_approved")))
        fsf_yes.append(sum(1 for l in group if l.get("metadata", {}).get("fsf_free")))
        fsf_no.append( sum(1 for l in group if not l.get("metadata", {}).get("fsf_free")))

    x     = np.arange(len(categories))
    width = 0.2
    ax.bar(x - 1.5*width, osi_yes, width, label="OSI ✅",  color="#4CAF50", edgecolor="#1E1E2E")
    ax.bar(x - 0.5*width, osi_no,  width, label="OSI ❌",  color="#EF5350", edgecolor="#1E1E2E")
    ax.bar(x + 0.5*width, fsf_yes, width, label="FSF ✅",  color="#42A5F5", edgecolor="#1E1E2E")
    ax.bar(x + 1.5*width, fsf_no,  width, label="FSF ❌",  color="#FF7043", edgecolor="#1E1E2E")

    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", "\n") for c in categories],
                       fontsize=8, color="white")
    ax.set_ylabel("Count", color="white", fontsize=9)
    ax.set_title("OSI & FSF Approval by License Type", color="white",
                 fontsize=11, fontweight="bold")
    ax.legend(facecolor="#2D2D3F", edgecolor="#555", labelcolor="white", fontsize=8)
    ax.yaxis.label.set_color("white")

    # ── [1,1] Stacked bar – permission coverage per type ─────────────────
    ax = axes[1, 1]
    permission_keys = ["commercial_use", "distribution", "modification", "private_use"]
    perm_labels     = ["Commercial", "Distribution", "Modification", "Private use"]
    perm_colors     = ["#66BB6A", "#42A5F5", "#FFA726", "#AB47BC"]

    type_perm_counts: dict[str, list[int]] = {cat: [0]*4 for cat in categories}
    type_totals: dict[str, int] = {cat: 0 for cat in categories}

    for l in licenses:
        cat = l.get("type", "")
        if cat not in type_perm_counts:
            continue
        type_totals[cat] += 1
        for i, pk in enumerate(permission_keys):
            if l.get("permissions", {}).get(pk):
                type_perm_counts[cat][i] += 1

    x      = np.arange(len(categories))
    bottom = np.zeros(len(categories))

    for i, (pk, pl, pc) in enumerate(zip(permission_keys, perm_labels, perm_colors)):
        heights = [
            (type_perm_counts[cat][i] / type_totals[cat] * 100)
            if type_totals[cat] else 0
            for cat in categories
        ]
        ax.bar(x, heights, width=0.55, bottom=bottom,
               label=pl, color=pc, edgecolor="#1E1E2E", linewidth=0.8)
        bottom += np.array(heights)

    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", "\n") for c in categories],
                       fontsize=8, color="white")
    ax.set_ylabel("% of licenses granting permission", color="white", fontsize=9)
    ax.set_title("Permission Coverage per License Type", color="white",
                 fontsize=11, fontweight="bold")
    ax.set_ylim(0, 420)
    ax.legend(facecolor="#2D2D3F", edgecolor="#555", labelcolor="white",
              fontsize=8, loc="upper right")
    ax.yaxis.label.set_color("white")

    fig.suptitle("LicenseWise – Knowledge Base Statistics",
                 fontsize=14, fontweight="bold", color="white", y=1.01)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Helper for missing dependency
# ---------------------------------------------------------------------------

def _missing_dep_figure(package: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor("#1E1E2E")
    ax.set_facecolor("#1E1E2E")
    ax.axis("off")
    ax.text(0.5, 0.5,
            f"Missing dependency: {package}\nInstall with:  pip install {package}",
            ha="center", va="center", fontsize=12, color="#EF5350",
            transform=ax.transAxes)
    return fig


# ---------------------------------------------------------------------------
# Gradio tab builder  (imported by gradio_app.py)
# ---------------------------------------------------------------------------

def build_graphs_tab(licenses: list[dict]) -> None:
    """
    Call this inside a gr.Blocks() context.
    Expects `licenses` to be the list already loaded by gradio_app.py.
    """
    import gradio as gr

    with gr.Tab("📊 Graphs"):
        gr.Markdown(
            "## Visual analysis of the license knowledge base\n"
            "All graphs are generated live from the loaded `licenses.json`."
        )

        with gr.Tabs():

            # ── Compatibility Matrix ─────────────────────────────────────
            with gr.Tab("Compatibility Matrix"):
                gr.Markdown(
                    "Pairwise compatibility heatmap.  \n"
                    "🟢 Compatible · 🟡 Partial / use-case dependent · 🔴 Incompatible"
                )
                max_slider = gr.Slider(5, 28, value=20, step=1,
                                       label="Max licenses to display")
                compat_btn = gr.Button("Generate matrix", variant="primary")
                compat_plot = gr.Plot(label="Compatibility Matrix")

                def _gen_compat(n):
                    return make_compatibility_matrix(licenses, max_licenses=int(n))

                compat_btn.click(_gen_compat, inputs=[max_slider], outputs=[compat_plot])

            # ── Dependency Graph ─────────────────────────────────────────
            with gr.Tab("Knowledge Graph"):
                gr.Markdown(
                    "Conceptual graph: **License Type → Conditions → Practical Outcomes**.  \n"
                    "Shows how each license type triggers certain legal conditions and "
                    "what that means in practice."
                )
                dep_btn  = gr.Button("Generate graph", variant="primary")
                dep_plot = gr.Plot(label="Knowledge Graph")
                dep_btn.click(lambda: make_dependency_graph(licenses),
                              inputs=[], outputs=[dep_plot])

            # ── Statistics ───────────────────────────────────────────────
            with gr.Tab("Statistics"):
                gr.Markdown(
                    "Four-panel statistics dashboard:  \n"
                    "type distribution · popularity ranking · OSI/FSF approval · permission coverage"
                )
                stat_btn  = gr.Button("Generate charts", variant="primary")
                stat_plot = gr.Plot(label="Statistics")
                stat_btn.click(lambda: make_statistics_charts(licenses),
                               inputs=[], outputs=[stat_plot])


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    REPO_ROOT     = Path(__file__).resolve().parent.parent
    LICENSES_PATH = REPO_ROOT / "_Licenses" / "licenses.json"
    FAMILIES_DIR  = REPO_ROOT / "_Licenses" / "Families"

    def _load():
        if LICENSES_PATH.exists():
            with open(LICENSES_PATH, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("licenses", data) if isinstance(data, dict) else data
        if FAMILIES_DIR.exists():
            seen, result = set(), []
            for p in sorted(FAMILIES_DIR.glob("*.json")):
                with open(p, encoding="utf-8") as f:
                    fd = json.load(f)
                for l in fd.get("licenses", []):
                    k = l.get("spdx_id") or l.get("id")
                    if k not in seen:
                        seen.add(k); result.append(l)
            return result
        return []

    lics = _load()
    print(f"Loaded {len(lics)} licenses")

    fig1 = make_compatibility_matrix(lics)
    fig2 = make_dependency_graph(lics)
    fig3 = make_statistics_charts(lics)
    plt.show()
