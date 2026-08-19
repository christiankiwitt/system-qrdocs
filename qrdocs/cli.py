import argparse
from pathlib import Path

from qrdocs.entries import load_entries, search_entries


DEFAULT_DATA_DIR = Path("/var/lib/system-qrdocs")


def print_entry(entry):
    location = entry.current_location or "Unknown"
    title = entry.title or "(untitled)"
    asset_id = entry.asset_id or "(no asset id)"

    print(f"{asset_id} — {title}")
    print(f"Current Location: {location}")


def main():
    parser = argparse.ArgumentParser(
        prog="qrdocs",
        description="Self-hosted QR-based asset documentation system",
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Canonical documentation data directory",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List documentation entries")

    search_parser = subparsers.add_parser(
        "search",
        help="Search documentation entries",
    )
    search_parser.add_argument(
        "terms",
        nargs="+",
        help="One or more search terms",
    )

    args = parser.parse_args()

    if args.command == "list":
        entries = load_entries(args.data_dir)

        if not entries:
            print("No documentation entries found.")
            return

        for entry in entries:
            print_entry(entry)
            print()

    elif args.command == "search":
        entries = load_entries(args.data_dir)
        matches = search_entries(entries, args.terms)

        if not matches:
            print("No matches found.")
            return

        for entry in matches:
            print_entry(entry)
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
