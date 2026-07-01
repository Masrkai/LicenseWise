"""Inference engine package for LicenseWise."""

from Inference.prolog_engine import PrologEngine

_engine = None


def get_engine() -> PrologEngine:
    """Return the singleton PrologEngine instance, creating it on first access."""
    global _engine
    if _engine is None:
        _engine = PrologEngine()
    return _engine
