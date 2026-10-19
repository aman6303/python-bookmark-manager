"""Data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Bookmark:
    """A saved bookmark."""

    id: Optional[int]
    title: str
    url: str
    tags: str = ""  # comma-separated
    category: str = ""
    description: str = ""
