"""Graph styling constants and data definitions for LicenseWise visualizations."""

from dataclasses import dataclass, field


@dataclass
class ThemeConfig:
    name: str = "dark"
    bg_color: str = "#1E1E2E"
    grid_color: str = "#444"
    edge_color: str = "#555577"
    legend_face: str = "#2D2D3F"
    legend_edge: str = "#555"
    text_color: str = "white"
    accent_color: str = "#90CAF9"
    type_colors: dict = field(default_factory=lambda: {
        "permissive": "#4CAF50",
        "weak_copyleft": "#FFC107",
        "copyleft": "#FF7043",
        "other": "#7986CB",
        "proprietary": "#EF5350",
    })
    default_color: str = "#90A4AE"
    font_title: int = 14
    font_label: int = 10
    font_tick: int = 8
    font_node_large: float = 7.5
    font_node_small: float = 6.5
    node_size_type: int = 1800
    node_size_condition: int = 1200
    node_size_outcome: int = 1500
    marker_condition: str = "D"
    marker_outcome: str = "s"
    color_condition: str = "#37474F"
    color_condition_edge: str = "#78909C"
    color_outcome: str = "#263238"
    color_outcome_edge: str = "#546E7A"
    text_condition: str = "#B0BEC5"
    text_outcome: str = "#CFD8DC"
    compat_cmap_colors: list = field(default_factory=lambda: ["#EF5350", "#FFC107", "#4CAF50"])

    @classmethod
    def dark(cls):
        return cls(name="dark")

    @classmethod
    def light(cls):
        return cls(
            name="light",
            bg_color="#f9fafb",
            grid_color="#d1d5db",
            edge_color="#9ca3af",
            legend_face="#ffffff",
            legend_edge="#d1d5db",
            text_color="#1e293b",
            accent_color="#4f46e5",
            color_condition="#e5e7eb",
            color_condition_edge="#9ca3af",
            color_outcome="#f3f4f6",
            color_outcome_edge="#9ca3af",
            text_condition="#374151",
            text_outcome="#1f2937",
            compat_cmap_colors=["#EF5350", "#FFC107", "#4CAF50"],
        )


_DARK = ThemeConfig.dark()

TYPE_COLORS = _DARK.type_colors
DEFAULT_COLOR = _DARK.default_color
BG_COLOR = _DARK.bg_color
GRID_COLOR = _DARK.grid_color
EDGE_COLOR = _DARK.edge_color
LEGEND_FACE = _DARK.legend_face
LEGEND_EDGE = _DARK.legend_edge
TEXT_COLOR = _DARK.text_color
ACCENT_COLOR = _DARK.accent_color
FONT_TITLE = _DARK.font_title
FONT_LABEL = _DARK.font_label
FONT_TICK = _DARK.font_tick
FONT_NODE_LARGE = _DARK.font_node_large
FONT_NODE_SMALL = _DARK.font_node_small
NODE_SIZE_TYPE = _DARK.node_size_type
NODE_SIZE_CONDITION = _DARK.node_size_condition
NODE_SIZE_OUTCOME = _DARK.node_size_outcome
MARKER_CONDITION = _DARK.marker_condition
MARKER_OUTCOME = _DARK.marker_outcome
COLOR_CONDITION = _DARK.color_condition
COLOR_CONDITION_EDGE = _DARK.color_condition_edge
COLOR_OUTCOME = _DARK.color_outcome
COLOR_OUTCOME_EDGE = _DARK.color_outcome_edge
TEXT_CONDITION = _DARK.text_condition
TEXT_OUTCOME = _DARK.text_outcome
COMPAT_CMAP_COLORS = _DARK.compat_cmap_colors

CONDITION_NODES = [
    "include_copyright",
    "document_changes",
    "disclose_source",
    "same_license",
    "net_copyleft",
]

OUTCOME_NODES = [
    "Can keep\nmodifications\nprivate",
    "Can use in\nproprietary\nproducts",
    "Can offer\nas SaaS",
    "Derivatives\nmust stay\nopen",
    "Full stack\ndisclosure\nrequired",
    "Patent\nprotection\ngranted",
]

TYPE_CONDITION_MAP = {
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

CONDITION_OUTCOME_EDGES = [
    ("disclose_source", "Derivatives\nmust stay\nopen"),
    ("same_license", "Derivatives\nmust stay\nopen"),
    ("net_copyleft", "Full stack\ndisclosure\nrequired"),
    ("net_copyleft", "Can offer\nas SaaS"),
    ("permissive", "Can keep\nmodifications\nprivate"),
    ("permissive", "Can use in\nproprietary\nproducts"),
    ("permissive", "Can offer\nas SaaS"),
    ("weak_copyleft", "Can use in\nproprietary\nproducts"),
    ("copyleft", "Derivatives\nmust stay\nopen"),
    ("proprietary", "Patent\nprotection\ngranted"),
]

LAYER_HEADERS = [("License Types", 0.0), ("Conditions", 0.45), ("Outcomes", 0.9)]

LAYER_X_TYPE = 0.0
LAYER_X_CONDITION = 0.45
LAYER_X_OUTCOME = 0.9
LAYER_Y_START_TYPE = 1.8
LAYER_Y_STEP_TYPE = 0.9
LAYER_Y_START_CONDITION = 1.8
LAYER_Y_STEP_CONDITION = 0.9
LAYER_Y_START_OUTCOME = 2.2
LAYER_Y_STEP_OUTCOME = 0.75
