"""Basic tests."""

import unittest

from bookmarks.services.bookmark_service import create_bookmark


class TestBookmarks(unittest.TestCase):
    def test_create_bookmark(self):
        bm = create_bookmark("Python Docs", "https://docs.python.org", "python,docs", "dev")
        self.assertEqual(bm.title, "Python Docs")
        self.assertTrue(bm.url.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
