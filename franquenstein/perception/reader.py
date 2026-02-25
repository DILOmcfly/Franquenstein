"""Document reader for Franquenstein external learning.

Supports .txt, .md, and .pdf (when pypdf is available).
"""

from __future__ import annotations

from pathlib import Path


def read_document(path: str) -> str:
    """Read a local document and return plain text.

    Args:
        path: Absolute or relative path to a supported file.

    Returns:
        Extracted text content.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If extension is unsupported.
    """
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    ext = p.suffix.lower()
    if ext in {".txt", ".md"}:
        return p.read_text(encoding="utf-8", errors="replace")

    if ext == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception as exc:
            raise ValueError(
                "PDF reading requires `pypdf`. Install with: pip install pypdf"
            ) from exc

        reader = PdfReader(str(p))
        chunks: list[str] = []
        for page in reader.pages:
            chunks.append(page.extract_text() or "")
        return "\n".join(chunks)

    raise ValueError(f"Unsupported file type: {ext}. Use .txt, .md, or .pdf")
