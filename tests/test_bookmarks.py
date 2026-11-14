"""Tests for bookmark service operations."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bookmarks.database as database
from bookmarks.database import init_db
from bookmarks.services.bookmark_service import (
    create_bookmark,
    find_bookmarks,
    list_bookmarks,
    open_bookmark,
    remove_bookmark,
)

class TestBookmarks(unittest.TestCase):
    """Unit test suite for bookmark operations and database persistence."""

    def setUp(self):
        """Runs BEFORE every individual test method.

        Creates an isolated temporary folder and redirects the database path
        so tests never touch the real database or leak data between runs.
        """
        # Create a disposable temporary directory on disk
        self.temp_dir = tempfile.TemporaryDirectory()

        # Monkeypatch the database file path to point to a new test DB inside the temp directory
        self.db_path_patch = patch.object(
            database, "DB_PATH", Path(self.temp_dir.name) / "bookmarks.db"
        )
        self.db_path_patch.start()

        # Build fresh database tables
        init_db()

    def tearDown(self):
        """Runs AFTER every individual test method.

        Cleans up patches and deletes temporary files.
        """
        # Stop mocking the DB path (restore the original setting)
        self.db_path_patch.stop()

        # Delete the temporary directory and all files inside it
        self.temp_dir.cleanup()

    # Creation Tests

    def test_create_bookmark_saves_all_fields(self):
        """Verify that a bookmark is saved with an auto-generated ID and all fields intact."""
        bookmark = create_bookmark(
            "Python Docs", "https://docs.python.org", "python,docs", "dev", "Reference"
        )

        self.assertIsNotNone(bookmark.id)
        self.assertEqual(bookmark.title, "Python Docs")
        self.assertEqual(bookmark.url, "https://docs.python.org")
        self.assertEqual(bookmark.tags, "python,docs")
        self.assertEqual(bookmark.category, "dev")
        self.assertEqual(bookmark.description, "Reference")

    # Listing & Retrieval Tests

    def test_list_bookmarks_returns_saved_bookmarks_sorted_by_title(self):
        """Verify that retrieving all bookmarks sorts them alphabetically by title."""
        # Insert out of order
        create_bookmark("Zebra", "https://z.example")
        create_bookmark("Apple", "https://a.example")

        bookmarks = list_bookmarks()

        # Expect sorted order: 'Apple' before 'Zebra'
        self.assertEqual([bookmark.title for bookmark in bookmarks], ["Apple", "Zebra"])

    def test_list_bookmarks_is_empty_when_no_bookmarks_exist(self):
        """Verify that list_bookmarks returns an empty list on a clean database."""
        self.assertEqual(list_bookmarks(), [])

    # Search Tests

    def test_find_bookmarks_matches_across_fields(self):
        """Verify keyword search matches across title, tags, description, and category."""
        create_bookmark(
            "Python Docs", "https://docs.python.org", "language", "learning", "tutorials"
        )
        create_bookmark("News", "https://news.example", "reading", "daily")

        # Match by description
        self.assertEqual([bm.title for bm in find_bookmarks("tutorials")], ["Python Docs"])
        # Match by tag / category
        self.assertEqual([bm.title for bm in find_bookmarks("reading")], ["News"])
        # No match should safely return an empty list
        self.assertEqual(find_bookmarks("no match"), [])

    # Deletion Tests

    def test_remove_bookmark_deletes_saved_bookmark(self):
        """Verify deleting an existing bookmark removes it completely from the database."""
        created = create_bookmark("Python Docs", "https://docs.python.org")
        assert created.id is not None

        # remove_bookmark should return True on successful deletion
        self.assertTrue(remove_bookmark(created.id))
        # Ensure it cannot be retrieved anymore
        self.assertIsNone(database.get_bookmark_by_id(created.id))
        self.assertEqual(list_bookmarks(), [])

    def test_remove_bookmark_returns_false_for_unknown_id(self):
        """Verify attempting to delete a non-existent bookmark returns False without error."""
        self.assertFalse(remove_bookmark(999))

    # Browser / Mocking Tests

    # @patch replaces webbrowser.open with a mock (passed into the test as `open_browser`).
    # This prevents an actual browser window from launching and allows verifying the call headlessly.
    @patch("bookmarks.services.bookmark_service.webbrowser.open")
    def test_open_bookmark_opens_saved_url(self, open_browser):
        """Verify opening a bookmark invokes webbrowser.open with the exact saved URL."""
        created = create_bookmark("Python Docs", "https://docs.python.org")
        assert created.id is not None

        self.assertTrue(open_bookmark(created.id))
        # Verify the mock was called exactly once with the expected URL
        open_browser.assert_called_once_with("https://docs.python.org")

    @patch("bookmarks.services.bookmark_service.webbrowser.open")
    def test_open_bookmark_returns_false_for_unknown_id(self, open_browser):
        """Verify that attempting to open a non-existent ID fails and never calls the browser."""
        self.assertFalse(open_bookmark(999))
        # Ensure the browser mock was never invoked
        open_browser.assert_not_called()


if __name__ == "__main__":
    unittest.main()
