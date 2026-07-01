"""Graph styling constants and data definitions for LicenseWise visualizations."""

# Colour palette
TYPE_COLORS = {
    "permissive": "#4CAF50",
    "weak_copyleft": "#FFC107",
    "copyleft": "#FF7043",
    "other": "#7986CB",
    "proprietary": "#EF5350",
}
DEFAULT_COLOR = "#90A4AE"

# Theme settings
BG_COLOR = "#1E1E2E"
GRID_COLOR = "#444"
EDGE_COLOR = "#555577"
LEGEND_FACE = "#2D2D3F"
LEGEND_EDGE = "#555"
TEXT_COLOR = "white"
ACCENT_COLOR = "#90CAF9"

# Font sizes
FONT_TITLE = 14
FONT_LABEL = 10
FONT_TICK = 8
FONT_NODE_LARGE = 7.5
FONT_NODE_SMALL = 6.5

# Node sizes
NODE_SIZE_TYPE = 1800
NODE_SIZE_CONDITION = 1200
NODE_SIZE_OUTCOME = 1500

# Node markers
MARKER_CONDITION = "D"
MARKER_OUTCOME = "s"

# Node colors
COLOR_CONDITION = "#37474F"
COLOR_CONDITION_EDGE = "#78909C"
COLOR_OUTCOME = "#263238"
COLOR_OUTCOME_EDGE = "#546E7A"
TEXT_CONDITION = "#B0BEC5"
TEXT_OUTCOME = "#CFD8DC"

# Knowledge graph node/edge definitions
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

# Column headers for knowledge graph
LAYER_HEADERS = [("License Types", 0.0), ("Conditions", 0.45), ("Outcomes", 0.9)]

# Layer layout positions
LAYER_X_TYPE = 0.0
LAYER_X_CONDITION = 0.45
LAYER_X_OUTCOME = 0.9
LAYER_Y_START_TYPE = 1.8
LAYER_Y_STEP_TYPE = 0.9
LAYER_Y_START_CONDITION = 1.8
LAYER_Y_STEP_CONDITION = 0.9
LAYER_Y_START_OUTCOME = 2.2
LAYER_Y_STEP_OUTCOME = 0.75

# Compatibility matrix colormap
COMPAT_CMAP_COLORS = ["#EF5350", "#FFC107", "#4CAF50"]
