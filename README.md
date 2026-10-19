# Local Bookmark Manager

A command-line tool to save, tag, search, and open bookmarks.  
Built with **only the Python standard library** (uses `webbrowser` to open links).

## Features

- Add, list, search, open, and delete bookmarks
- Tags and categories
- Opens links in your default browser
- Interactive menu + direct commands
- Pure standard library

## Project Structure

```
bookmark-manager/
├── src/
│   └── bookmarks/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── models.py
│       ├── database.py
│       └── services/
│           └── bookmark_service.py
├── data/          # SQLite database created here
├── tests/
├── pyproject.toml
├── README.md
└── .gitignore
```

## Requirements

- Python 3.12 or higher (recommended: 3.15)
- No external packages

## Setup (Recommended: Virtual Environment)

**Recommended tool: [uv](https://docs.astral.sh/uv/)** (fast, modern, industry-grade).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.15
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows
uv pip install -e .                # optional
```

Other options: `python -m venv .venv`, Poetry, or conda.

## How to Run

Two ways of working:

1. **Interactive menu** (best for beginners)
   ```bash
   python -m bookmarks.main
   ```

2. **Direct commands**

```bash
# Show all commands + required arguments
python -m bookmarks.main commands
```

### Examples

```bash
# Add a bookmark
python -m bookmarks.main add "Python Docs" "https://docs.python.org" --tags "python,docs" --category "dev"

# List all bookmarks
python -m bookmarks.main list

# Open a bookmark in browser
python -m bookmarks.main open 1

# Search
python -m bookmarks.main search python

# Delete
python -m bookmarks.main delete 1
```

## Running Tests

```bash
python -m unittest tests/test_bookmarks.py
```

## Teaching Notes

Demonstrates:
- SQLite storage
- Using the `webbrowser` standard library module
- Search across multiple fields
- Interactive menu + subcommand CLI
- Clean project structure

## License

Educational use only.
