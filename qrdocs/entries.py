from dataclasses import dataclass
from pathlib import Path


@dataclass
class Entry:
    path: Path
    title: str
    asset_id: str
    current_location: str
    text: str


def _section_value(lines: list[str], heading: str) -> str:
    target = f"### {heading}".casefold()

    for index, line in enumerate(lines):
        if line.strip().casefold() == target:
            for value_line in lines[index + 1:]:
                value = value_line.strip()

                if value.startswith("#"):
                    break

                if value:
                    return value

    return ""


def read_entry(path: Path) -> Entry:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = ""
    asset_id = ""

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()

        elif stripped.startswith("## ") and not asset_id:
            asset_id = stripped[3:].strip()

        if title and asset_id:
            break

    current_location = _section_value(lines, "Current Location")

    return Entry(
        path=path,
        title=title,
        asset_id=asset_id,
        current_location=current_location,
        text=text,
    )


def load_entries(data_dir: Path) -> list[Entry]:
    if not data_dir.exists():
        return []

    entries = []

    for path in sorted(data_dir.rglob("*.md")):
        if not path.is_file():
            continue

        relative = path.relative_to(data_dir)

        if relative.parts and relative.parts[0].casefold() == "public":
            continue

        entries.append(read_entry(path))

    return entries


def search_entries(
    entries: list[Entry],
    terms: list[str],
    *,
    loose: bool = False,
) -> list[Entry]:
    def normalize(value: str) -> str:
        value = value.casefold()

        if not loose:
            return value

        return "".join(
            character
            for character in value
            if character.isalnum() or character.isspace()
        )

    normalized_terms = [
        normalize(term)
        for term in terms
    ]

    matches = []

    for entry in entries:
        haystack = normalize(entry.text)

        if all(term in haystack for term in normalized_terms):
            matches.append(entry)

    return matches
