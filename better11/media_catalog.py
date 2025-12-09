"""Media catalog modeling and validation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List
import json


@dataclass
class MediaItem:
    """Representation of a media item entry."""

    identifier: str
    url: str


@dataclass
class MediaCatalog:
    """Container for media items."""

    items: List[MediaItem]

    @classmethod
    def load(cls, raw: str) -> "MediaCatalog":
        """Create a catalog from a JSON payload.

        The expected payload structure is a mapping with an ``items`` key
        containing a list of objects. Each object must provide both an
        ``id`` and ``url`` field. A ``ValueError`` is raised when required
        fields are missing or the structure is incorrect.
        """

        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("Catalog payload must be a JSON object")

        items = payload.get("items")
        if not isinstance(items, list):
            raise ValueError("Catalog payload must include an 'items' list")

        parsed_items: List[MediaItem] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"Item at index {index} must be an object")

            identifier = item.get("id")
            url = item.get("url")
            if not identifier or not url:
                raise ValueError(
                    f"Item at index {index} is missing required fields 'id' and 'url'"
                )

            parsed_items.append(MediaItem(identifier=str(identifier), url=str(url)))

        return cls(items=parsed_items)
