"""Tests for CLI arguments, help commands, and error handling."""

import io
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bookmarks.database as database
from bookmarks.database import init_db
from bookmarks.main import main, preprocess_args


def strip_ansi(text: str) -> str:
    """Strip ANSI color/formatting codes to inspect pure plain text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


class TestCLIHelp(unittest.TestCase):
    """Test suite for CLI help syntax and argument validation."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path_patch = patch.object(
            database, "DB_PATH", Path(self.temp_dir.name) / "bookmarks.db"
        )
        self.db_path_patch.start()
        # Disable ANSI color sequences in Python 3.14+ terminal output during tests
        self.env_patch = patch.dict(
            "os.environ", {"NO_COLOR": "1", "PYTHON_COLORS": "0"}
        )
        self.env_patch.start()
        init_db()

    def tearDown(self):
        self.env_patch.stop()
        self.db_path_patch.stop()
        self.temp_dir.cleanup()

    def test_preprocess_args(self):
        self.assertEqual(preprocess_args([]), [])
        self.assertEqual(preprocess_args(["-help"]), ["--help"])
        self.assertEqual(preprocess_args(["-h", "add"]), ["help", "add"])
        self.assertEqual(preprocess_args(["--help", "add"]), ["help", "add"])
        self.assertEqual(preprocess_args(["-help", "add"]), ["help", "add"])
        self.assertEqual(preprocess_args(["-help", "delete"]), ["help", "delete"])
        self.assertEqual(preprocess_args(["add", "-help"]), ["add", "--help"])
        self.assertEqual(preprocess_args(["delete", "-help"]), ["delete", "--help"])

    def test_general_help_command(self):
        """Verify that 'help' command outputs general help listing subcommands."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            main(["help"])

        output = strip_ansi(captured.getvalue())
        self.assertIn("usage: bookmarks", output)
        self.assertIn("add", output)
        self.assertIn("delete", output)
        self.assertIn("search", output)
        self.assertIn("list", output)

    def test_help_specific_command_add(self):
        """Verify that 'help add', '-help add', '-h add', and '--help add' print add help."""
        for args in (["help", "add"], ["-help", "add"], ["-h", "add"], ["--help", "add"]):
            with self.subTest(args=args):
                captured = io.StringIO()
                with patch("sys.stdout", captured):
                    main(args)

                output = strip_ansi(captured.getvalue())
                self.assertIn("usage: bookmarks add", output)
                self.assertIn("title", output)
                self.assertIn("url", output)
                self.assertIn("--tags", output)
                self.assertIn("--category", output)
                self.assertIn("--desc", output)

    def test_help_specific_command_delete(self):
        """Verify that 'help delete' and '-help delete' print delete help showing required ID."""
        for args in (["help", "delete"], ["-help", "delete"]):
            with self.subTest(args=args):
                captured = io.StringIO()
                with patch("sys.stdout", captured):
                    main(args)

                output = strip_ansi(captured.getvalue())
                self.assertIn("usage: bookmarks delete", output)
                self.assertIn("id", output)

    def test_missing_args_add_prints_full_help_and_error(self):
        """Verify running 'add' directly with missing arguments outputs help and error."""
        captured_err = io.StringIO()
        with patch("sys.stderr", captured_err):
            with self.assertRaises(SystemExit) as ctx:
                main(["add"])

        self.assertEqual(ctx.exception.code, 2)
        err_output = strip_ansi(captured_err.getvalue())
        self.assertIn("usage: bookmarks add", err_output)
        self.assertIn("title", err_output)
        self.assertIn("url", err_output)
        self.assertIn("Error: the following arguments are required: title, url", err_output)

    def test_missing_args_delete_prints_full_help_and_error(self):
        """Verify running 'delete' directly with missing arguments outputs help and error."""
        captured_err = io.StringIO()
        with patch("sys.stderr", captured_err):
            with self.assertRaises(SystemExit) as ctx:
                main(["delete"])

        self.assertEqual(ctx.exception.code, 2)
        err_output = strip_ansi(captured_err.getvalue())
        self.assertIn("usage: bookmarks delete", err_output)
        self.assertIn("id", err_output)
        self.assertIn("Error: the following arguments are required: id", err_output)

    def test_help_unknown_command(self):
        """Verify that 'help <unknown>' displays unknown command and lists available commands."""
        captured_out = io.StringIO()
        with patch("sys.stdout", captured_out):
            with self.assertRaises(SystemExit) as ctx:
                main(["help", "unknown_cmd"])

        self.assertEqual(ctx.exception.code, 2)
        output = strip_ansi(captured_out.getvalue())
        self.assertIn("Unknown command 'unknown_cmd'", output)
        self.assertIn("Available commands: add, delete, list, menu, open, search", output)

    def test_direct_crud_commands(self):
        """Verify direct CRUD execution via CLI."""
        # Add bookmark
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            main(["add", "Example", "https://example.com", "--tags", "test", "--category", "demo"])
        self.assertIn("Added bookmark 'Example'", strip_ansi(captured.getvalue()))

        # List bookmarks
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            main(["list"])
        self.assertIn("Example", strip_ansi(captured.getvalue()))
        self.assertIn("https://example.com", strip_ansi(captured.getvalue()))

        # Search bookmarks
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            main(["search", "Example"])
        self.assertIn("Found 1 bookmark(s)", strip_ansi(captured.getvalue()))

        # Delete bookmark
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            main(["delete", "1"])
        self.assertIn("Bookmark 1 deleted", strip_ansi(captured.getvalue()))


if __name__ == "__main__":
    unittest.main()
