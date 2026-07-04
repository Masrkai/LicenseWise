"""Inference engine package for LicenseWise."""

from .prolog_engine import PrologEngine

_engine: PrologEngine | None = None


def get_engine() -> PrologEngine:
    """Return the singleton PrologEngine instance, creating it on first access."""
    global _engine
    if _engine is None:
        _engine = PrologEngine()
    return _engine
