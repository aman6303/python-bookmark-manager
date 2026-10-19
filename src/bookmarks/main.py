"""CLI for the Bookmark Manager."""

import argparse

from bookmarks.database import init_db
from bookmarks.services.bookmark_service import (
    create_bookmark,
    find_bookmarks,
    get_bookmark,
    list_bookmarks,
    open_bookmark,
    remove_bookmark,
)


def print_detailed_commands() -> None:
    print("Local Bookmark Manager – Available Commands\n")
    print("Usage: python -m bookmarks.main <command> [arguments]\n")
    print("Commands:")
    print("  add TITLE URL [--tags TAGS] [--category CAT] [--desc TEXT]")
    print("      Add a new bookmark\n")
    print("  list")
    print("      List all bookmarks\n")
    print("  open ID")
    print("      Open bookmark in default browser\n")
    print("  search QUERY")
    print("      Search bookmarks\n")
    print("  delete ID")
    print("      Delete a bookmark\n")
    print("  commands")
    print("      Show this detailed list\n")
    print("  menu")
    print("      Start interactive menu\n")


def interactive_menu() -> None:
    print("\n=== Local Bookmark Manager ===")
    print("Interactive mode (type a number or 'q' to quit)\n")

    while True:
        print("1. Add bookmark")
        print("2. List bookmarks")
        print("3. Open bookmark")
        print("4. Search bookmarks")
        print("5. Delete bookmark")
        print("6. Show all commands")
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
                print(f"\n{'ID':<5} {'Title':<30} {'Category':<15} URL")
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

        elif choice == "6":
            print_detailed_commands()
            print()

        elif choice in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")


def main() -> None:
    init_db()

    parser = argparse.ArgumentParser(description="Local Bookmark Manager (stdlib only)")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    add_p = subparsers.add_parser("add", help="Add a new bookmark")
    add_p.add_argument("title", help="Bookmark title")
    add_p.add_argument("url", help="URL")
    add_p.add_argument("--tags", default="", help="Comma-separated tags")
    add_p.add_argument("--category", default="", help="Category")
    add_p.add_argument("--desc", default="", help="Description")

    subparsers.add_parser("list", help="List all bookmarks")

    open_p = subparsers.add_parser("open", help="Open bookmark in browser")
    open_p.add_argument("id", type=int, help="Bookmark ID")

    search_p = subparsers.add_parser("search", help="Search bookmarks")
    search_p.add_argument("query", help="Search term")

    del_p = subparsers.add_parser("delete", help="Delete a bookmark")
    del_p.add_argument("id", type=int, help="Bookmark ID")

    subparsers.add_parser("commands", help="Show all commands with arguments")
    subparsers.add_parser("menu", help="Start interactive menu")

    args = parser.parse_args()

    if not args.command:
        interactive_menu()
        return

    if args.command == "commands":
        print_detailed_commands()
        return

    if args.command == "menu":
        interactive_menu()
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
