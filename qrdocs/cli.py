import argparse
from pathlib import Path

from qrdocs.entries import load_entries, search_entries


DEFAULT_DATA_DIR = Path("/var/lib/system-qrdocs")
TEMPLATE_DIR = Path(__file__).parent / "templates"


def print_entry(entry):
    location = entry.current_location or "Unknown"
    title = entry.title or "(untitled)"
    asset_id = entry.asset_id or "(no asset id)"

    print(f"{asset_id} — {title}")
    print(f"Current Location: {location}")


def create_entry(data_dir: Path, entry_type: str, asset_id: str, title: str) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)

    existing_ids = {
        entry.asset_id.casefold()
        for entry in load_entries(data_dir)
        if entry.asset_id
    }

    if asset_id.casefold() in existing_ids:
        raise ValueError(f"Asset ID already exists: {asset_id}")

    template_name = "box.md" if entry_type == "box" else "asset.md"
    template_path = TEMPLATE_DIR / template_name

    text = template_path.read_text(encoding="utf-8")
    text = text.replace("# Title", f"# {title}", 1)

    if entry_type == "box":
        text = text.replace("## BOX-ID", f"## {asset_id}", 1)
    else:
        text = text.replace("## ITEM-ID", f"## {asset_id}", 1)

    output_path = data_dir / f"{asset_id}.md"

    if output_path.exists():
        raise ValueError(f"File already exists: {output_path}")

    output_path.write_text(text, encoding="utf-8")
    return output_path


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

    new_parser = subparsers.add_parser(
        "new",
        help="Create a new documentation entry",
    )
    new_parser.add_argument(
        "type",
        choices=["item", "box"],
        help="Entry type",
    )
    new_parser.add_argument(
        "asset_id",
        help="Permanent Asset ID",
    )
    new_parser.add_argument(
        "title",
        help="Entry title",
    )

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

    if args.command == "new":
        try:
            path = create_entry(
                data_dir=args.data_dir,
                entry_type=args.type,
                asset_id=args.asset_id,
                title=args.title,
            )
        except ValueError as exc:
            parser.error(str(exc))

        print(f"Created: {path}")

    elif args.command == "list":
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
