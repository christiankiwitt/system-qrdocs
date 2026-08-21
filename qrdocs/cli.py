import argparse
import os
import shlex
import subprocess
from pathlib import Path
from qrdocs.public import (
    build_public_asset,
    public_source_path,
    public_url_path,
)
from qrdocs.entries import load_entries, search_entries
from qrdocs.build import build_private_site
from qrdocs.labels import generate_label_pdf
from qrdocs.config import DEFAULT_CONFIG_PATH, get_public_base_url, load_config


DEFAULT_DATA_DIR = Path("/var/lib/system-qrdocs")
TEMPLATE_DIR = Path(__file__).parent / "templates"


def print_entry(entry):
    location = entry.current_location or "Unknown"
    title = entry.title or "(untitled)"
    asset_id = entry.asset_id or "(no asset id)"

    print(f"{asset_id} - {title}")
    print(f"Current Location: {location}")


def open_in_editor(path: Path) -> None:
    editor = os.environ.get("EDITOR", "nano")
    command = shlex.split(editor) + [str(path)]
    subprocess.run(command, check=True)


def find_entry(data_dir: Path, asset_id: str):
    target = asset_id.casefold()

    for entry in load_entries(data_dir):
        if entry.asset_id.casefold() == target:
            return entry

    return None


def create_entry(
    data_dir: Path,
    entry_type: str,
    asset_id: str,
    title: str,
) -> Path:
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

def confirm(prompt: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        answer = input(prompt + suffix).strip().casefold()

        if not answer:
            return default

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Please answer y or n.")

def create_public_source(
    data_dir: Path,
    asset_id: str,
    title: str,
) -> Path:
    existing = public_source_path(data_dir, asset_id)

    if existing is not None:
        return existing

    public_dir = data_dir / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    path = public_dir / f"{asset_id}.md"

    text = (
        f"# {title}\n\n"
        f"## {asset_id}\n\n"
        "Public information goes here.\n"
    )

    path.write_text(text, encoding="utf-8")
    return path

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

    rebuild_parser = subparsers.add_parser(
        "rebuild",
        help="Build the private HTML documentation site",
    )
    rebuild_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/var/www/system-qrdocs/private"),
        help="Private HTML output directory",
    )

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
    new_parser.add_argument(
        "--no-edit",
        action="store_true",
        help="Create the entry without opening it in the editor",
    )

    edit_parser = subparsers.add_parser(
        "edit",
        help="Edit an existing documentation entry",
    )
    edit_parser.add_argument(
        "asset_id",
        help="Asset ID to edit",
    )

    label_parser = subparsers.add_parser(
        "label",
        help="Generate a printable QR label PDF",
    )
    label_parser.add_argument(
        "asset_id",
        help="Asset ID to generate a label for",
    )
    label_parser.add_argument(
        "--url",
        help="Override the URL encoded in the QR code",
    )
    label_parser.add_argument(
        "--output",
        type=Path,
        default=Path("label.pdf"),
        help="Output PDF path",
    )

    public_parser = subparsers.add_parser(
        "public",
        help="Build the public page for an asset",
    )
    public_parser.add_argument(
        "asset_id",
        help="Asset ID to publish",
    )
    public_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/var/www/system-qrdocs-public"),
        help="Public HTML output directory",
    )

    subparsers.add_parser(
        "list",
        help="List documentation entries",
    )

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
    config = load_config(DEFAULT_CONFIG_PATH)
    public_base_url = get_public_base_url(config)

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

        if not args.no_edit:
            open_in_editor(path)

        if confirm("Create a public page for this entry?", default=False):
            public_path = create_public_source(
                data_dir=args.data_dir,
                asset_id=args.asset_id,
                title=args.title,
            )

            print(f"Created public source: {public_path}")
            open_in_editor(public_path)

    elif args.command == "edit":
        entry = find_entry(args.data_dir, args.asset_id)

        if entry is None:
            parser.error(f"Asset ID not found: {args.asset_id}")

        open_in_editor(entry.path)

        public_path = public_source_path(args.data_dir, args.asset_id)

        if public_path is None:
            print("Public page: DISABLED")

            if confirm("Create a public page for this entry?", default=False):
                public_path = create_public_source(
                    data_dir=args.data_dir,
                    asset_id=entry.asset_id,
                    title=entry.title or "(untitled)",
                )

                print(f"Created public source: {public_path}")
                open_in_editor(public_path)

        else:
            print(f"Public page: ENABLED ({public_path})")

            if confirm("Edit the public page too?", default=False):
                open_in_editor(public_path)

    elif args.command == "label":
        entry = find_entry(args.data_dir, args.asset_id)

        if entry is None:
            parser.error(f"Asset ID not found: {args.asset_id}")

        url = args.url

        if not url:
            if not public_base_url:
                parser.error(
                    "No URL supplied and no public.base_url configured."
                )

            url = f"{public_base_url}{public_url_path(args.data_dir, args.asset_id)}"

        path = generate_label_pdf(
            asset_id=entry.asset_id,
            title=entry.title or "(untitled)",
            url=url,
            output_path=args.output,
        )

        print(f"Created: {path}")
        print(f"QR URL: {url}")

    elif args.command == "public":
        try:
            path = build_public_asset(
                data_dir=args.data_dir,
                asset_id=args.asset_id,
                output_dir=args.output_dir,
            )
        except FileNotFoundError as exc:
            parser.error(str(exc))

        print(f"Built public page: {path}")

        url_path = public_url_path(args.data_dir, args.asset_id)
        print(f"Public URL path: {url_path}")

        if public_base_url:
            print(f"Public URL: {public_base_url}{url_path}")

    elif args.command == "rebuild":
        count = build_private_site(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
        )
        print(f"Built {count} documentation entries.")

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