"""Report string templates for LicenseWise explanation engine."""

REPORT_HEADER = "LICENSEWISE FINAL REPORT"
SECTION_RECOMMENDED = "RECOMMENDED LICENSES:"
SECTION_ELIMINATED = "ELIMINATED LICENSES:"
SECTION_WARNINGS = "WARNINGS:"
SECTION_CONFIDENCE = "CONFIDENCE:"
TRACE_HEADER = "HOW THE ENGINE REACHED THIS CONCLUSION:"
SUMMARY_HEADER = "EXPLANATION: How did the engine get this result?"
DISCLAIMER = "DISCLAIMER: This is not legal advice. Consult a lawyer for production use."
NO_LICENSES_RECOMMENDED = "\nNo licenses were recommended. Please review your project goals."
NO_RULES_FIRED = "No rules were fired during inference."
SUMMARY_RECOMMENDED = "The engine RECOMMENDED licenses because:"
SUMMARY_ELIMINATED = "The engine ELIMINATED licenses because:"
SUMMARY_WARNED = "The engine WARNED because:"
SUMMARY_FOOTER = "Each step above was triggered by matching your answers against the rule base."
SEP = "=" * 60
SEP_SHORT = "-" * 50

TRACE_ACTION_ICONS = {
    "RECOMMEND": "+",
    "ELIMINATE": "x",
    "WARN": "!",
}
