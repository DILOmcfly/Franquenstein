"""Perception modules for external knowledge ingestion."""

from .reader import read_document
from .web import fetch_web_text

__all__ = ["read_document", "fetch_web_text"]
