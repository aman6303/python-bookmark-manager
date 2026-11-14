"""Configuration and data paths."""

import os
from pathlib import Path

# Allow overriding the database location via environment variable
CUSTOM_DB_PATH = os.environ.get("BOOKMARKS_DB_PATH")

if CUSTOM_DB_PATH:
    DB_PATH = Path(CUSTOM_DB_PATH).expanduser().resolve()
    DATA_DIR = DB_PATH.parent
else:
    # Use local 'data/' directory if running from repository root,
    # otherwise fallback to user home directory (~/.bookmarks) when installed
    repo_data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    if repo_data_dir.exists():
        DATA_DIR = repo_data_dir
    else:
        DATA_DIR = Path.home() / ".bookmarks"

    DB_PATH = DATA_DIR / "bookmarks.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
