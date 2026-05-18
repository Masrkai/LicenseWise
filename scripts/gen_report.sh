#!/usr/bin/env bash
# build_report.sh – Combine docs into a PDF in the order given.
# Run from the project root. Markdown sources are in docs/Current/.

set -euo pipefail

DOCS="Docs/Current"

pandoc -o report.pdf --pdf-engine=xelatex --resource-path=$DOCS \
  -f markdown+tex_math_single_backslash+tex_math_double_backslash+tex_math_dollars+raw_tex+smart \
  -V geometry:"a4paper, margin=1.5cm" -V fontsize=12pt -V  mainfont="FreeSans" --filter pandoc-include --lua-filter="$PANDOC_DIAGRAM_FILTER" \


  "$DOCS/team_members.md" \
  "$DOCS/requirements_checked.md" \
  "$DOCS/DataSources.md" \
  "$DOCS/src_ClubSystem.md" \
  "$DOCS/src_DatabaseHandler.md" \
  "$DOCS/src_ClubManagementService.md" \
  "$DOCS/src_Main.md" \
  "$DOCS/src_ClubManagementGUI.md" \
  "$DOCS/src_SortingAlgorithms.md" \
  "$DOCS/src_BinarySearch.md" \
  "$DOCS/Algorithm_complexity.md" \
  "$DOCS/BuildSystem.md"

echo "✅ PDF generated: report.pdf"