"""Source attribution records for provenance tracking (v0.4.0+).

A :class:`SourceRecord` captures the **raw (pre-merge) extraction results**
of one source document, plus an optional content hash for change detection.
Records live in OMem's source ledger (``OMem(track_sources=True)``) and are
the foundation for exact per-document rollback: because merges are
destructive, the only way to remove a source's contributions precisely is to
re-merge the surviving sources' raw results for the affected keys.
"""

from typing import Any

from pydantic import BaseModel


class SourceRecord(BaseModel):
    """Ledger entry for one attributed source.

    Attributes:
        source_id: Caller-chosen identifier (e.g. a document path or id).
        content_hash: Optional hash of the source content — used to skip
            re-processing when the content is unchanged.
        raw_items: The source's raw items as ``model_dump()`` dicts
            (pre-merge). Stored as dicts so the ledger persists to JSON
            without custom encoders; re-materialize with the owning OMem's
            ``memory_schema``.
    """

    source_id: str
    content_hash: str | None = None
    raw_items: list[dict[str, Any]] = []

    @property
    def size(self) -> int:
        """Number of raw items captured from this source."""
        return len(self.raw_items)
