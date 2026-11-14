"""CLI for the Bookmark Manager."""

import argparse
import sys
from typing import List, NoReturn, Optional, Tuple

from bookmarks.database import init_db
from bookmarks.services.bookmark_service import (
    create_bookmark,
    find_bookmarks,
    list_bookmarks,
    open_bookmark,
    remove_bookmark,
)


class HelpfulArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that outputs full help when an argument error occurs."""

    def error(self, message: str) -> NoReturn:
        self.print_help(sys.stderr)               # 1. Print full instructions first!
        sys.stderr.write(f"\nError: {message}\n") # 2. Print the error at the bottom
        sys.exit(2)                               # 3. Stop the program


def preprocess_args(args: List[str]) -> List[str]:
    """Normalize command-line arguments to support flexible help syntax.

    Supports:
    - '-h <command>', '--help <command>', '-help <command>' -> ['help', '<command>']
    - '-help' -> '--help'
    - '<command> -help' -> ['<command>', '--help']
    """
    if not args:
        return args

    # If the user typed '-help add' or '-h add', change it to 'help add'
    if len(args) >= 2 and args[0] in ("-h", "--help", "-help"):
        return ["help", args[1]]
    
    # If the user typed a single '-help', make it standard '--help'
    return ["--help" if a == "-help" else a for a in args]


def build_parser() -> Tuple[HelpfulArgumentParser, argparse._SubParsersAction]:
    """Build and configure the CLI argument parser with subparsers."""
    parser = HelpfulArgumentParser(
        prog="bookmarks",
        description="Local Bookmark Manager - Save, tag, search, and manage your bookmarks.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Commands",
        parser_class=HelpfulArgumentParser,
    )

    # add command
    add_p = subparsers.add_parser(
        "add",
        help="Add a new bookmark",
        description="Add a new bookmark to your collection.",
    )
    add_p.add_argument("title", help="Bookmark title")
    add_p.add_argument("url", help="URL of the bookmark")
    add_p.add_argument("--tags", default="", help="Comma-separated tags (optional)")
    add_p.add_argument("--category", default="", help="Bookmark category (optional)")
    add_p.add_argument("--desc", default="", help="Bookmark description (optional)")

    # list command
    subparsers.add_parser(
        "list",
        help="List all bookmarks",
        description="List all saved bookmarks sorted alphabetically by title.",
    )

    # open command
    open_p = subparsers.add_parser(
        "open",
        help="Open bookmark in browser",
        description="Open a bookmark in your default web browser by its ID.",
    )
    open_p.add_argument("id", type=int, help="Bookmark ID to open")

    # search command
    search_p = subparsers.add_parser(
        "search",
        help="Search bookmarks",
        description="Search bookmarks by title, URL, tags, category, or description.",
    )
    search_p.add_argument("query", help="Search keyword or term")

    # delete command
    del_p = subparsers.add_parser(
        "delete",
        help="Delete a bookmark",
        description="Delete a bookmark from the database by its ID.",
    )
    del_p.add_argument("id", type=int, help="Bookmark ID to delete")

    # menu command
    subparsers.add_parser(
        "menu",
        help="Start interactive menu",
        description="Start the interactive menu mode.",
    )

    # help command
    help_p = subparsers.add_parser(
        "help",
        help="Show help for a command",
        description="Show general help or detailed help for a specific command.",
    )
    help_p.add_argument(
        "subcommand",
        nargs="?",
        help="Command to get help for (e.g. add, delete, list, open, search)",
    )

    return parser, subparsers

def interactive_menu() -> None:
    print("\n=== Local Bookmark Manager ===")
    print("Interactive mode (type a number or 'q' to quit)\n")

    while True:
        print("1. Add bookmark")
        print("2. List bookmarks")
        print("3. Open bookmark")
        print("4. Search bookmarks")
        print("5. Delete bookmark")
        print("q. Quit")
        choice = input("\nChoose an option: ").strip().lower()

        if choice == "1":
            title = input("Title: ").strip()
            url = input("URL: ").strip()
            tags = input("Tags (comma-separated, optional): ").strip()
            category = input("Category (optional): ").strip()
            description = input("Description (optional): ").strip()
            if not title or not url:
                print("Title and URL are required.\n")
                continue
            bm = create_bookmark(title, url, tags, category, description)
            print(f"Added bookmark '{bm.title}' (ID: {bm.id})\n")

        elif choice == "2":
            bookmarks = list_bookmarks()
            if not bookmarks:
                print("No bookmarks yet.\n")
            else:
                print(f"\n{'ID':5} {'Title':<30} {'Category':<15} URL")
                print("-" * 80)
                for bm in bookmarks:
                    print(f"{bm.id:<5} {bm.title:<30} {bm.category:<15} {bm.url}")
                print()

        elif choice == "3":
            try:
                bid = int(input("Bookmark ID: ").strip())
                if open_bookmark(bid):
                    print("Opened in browser.\n")
                else:
                    print("Bookmark not found.\n")
            except ValueError:
                print("Invalid ID.\n")

        elif choice == "4":
            query = input("Search term: ").strip()
            results = find_bookmarks(query)
            if not results:
                print("No matches.\n")
            else:
                print(f"\nFound {len(results)} bookmark(s):")
                for bm in results:
                    print(f"  [{bm.id}] {bm.title} - {bm.url}")
                print()

        elif choice == "5":
            try:
                bid = int(input("Bookmark ID to delete: ").strip())
                if remove_bookmark(bid):
                    print("Bookmark deleted.\n")
                else:
                    print("Bookmark not found.\n")
            except ValueError:
                print("Invalid ID.\n")

        elif choice in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")


def main(argv: Optional[List[str]] = None) -> None:
    init_db()

    parser, subparsers = build_parser()

    if argv is None:
        argv = sys.argv[1:]

    processed_argv = preprocess_args(argv)
    args = parser.parse_args(processed_argv)

    if not args.command or args.command == "menu":
        interactive_menu()
        return

    if args.command == "help":
        if args.subcommand:
            sub = subparsers.choices.get(args.subcommand)
            if sub:
                sub.print_help()
            else:
                available = ", ".join(sorted(cmd for cmd in subparsers.choices.keys() if cmd != "help"))
                print(f"Unknown command '{args.subcommand}'.")
                print(f"Available commands: {available}\n")
                parser.print_help()
                sys.exit(2)
        else:
            parser.print_help()
        return

    if args.command == "add":
        bm = create_bookmark(args.title, args.url, args.tags, args.category, args.desc)
        print(f"Added bookmark '{bm.title}' (ID: {bm.id})")

    elif args.command == "list":
        bookmarks = list_bookmarks()
        if not bookmarks:
            print("No bookmarks yet.")
            return
        print(f"{'ID':<5} {'Title':<30} {'Category':<15} URL")
        print("-" * 80)
        for bm in bookmarks:
            print(f"{bm.id:<5} {bm.title:<30} {bm.category:<15} {bm.url}")

    elif args.command == "open":
        if open_bookmark(args.id):
            print(f"Opened bookmark {args.id} in browser.")
        else:
            print("Bookmark not found.")

    elif args.command == "search":
        results = find_bookmarks(args.query)
        if not results:
            print("No matches.")
            return
        print(f"Found {len(results)} bookmark(s):")
        for bm in results:
            print(f"  [{bm.id}] {bm.title} - {bm.url}")

    elif args.command == "delete":
        if remove_bookmark(args.id):
            print(f"Bookmark {args.id} deleted.")
        else:
            print("Bookmark not found.")


if __name__ == "__main__":
    main()
