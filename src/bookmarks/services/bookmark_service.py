"""Bookmark business logic."""

import webbrowser
from typing import List, Optional

from bookmarks.database import (
    add_bookmark as db_add,
    delete_bookmark as db_delete,
    get_all_bookmarks,
    get_bookmark_by_id,
    search_bookmarks as db_search,
)
from bookmarks.models import Bookmark


def create_bookmark(title: str, url: str, tags: str = "", category: str = "", description: str = "") -> Bookmark:
    bid = db_add(title, url, tags, category, description)
    return Bookmark(id=bid, title=title, url=url, tags=tags, category=category, description=description)


def list_bookmarks() -> List[Bookmark]:
    return get_all_bookmarks()


def find_bookmarks(query: str) -> List[Bookmark]:
    return db_search(query)


def get_bookmark(bookmark_id: int) -> Optional[Bookmark]:
    return get_bookmark_by_id(bookmark_id)


def open_bookmark(bookmark_id: int) -> bool:
    bm = get_bookmark_by_id(bookmark_id)
    if not bm:
        return False
    webbrowser.open(bm.url)
    return True


def remove_bookmark(bookmark_id: int) -> bool:
    return db_delete(bookmark_id)
