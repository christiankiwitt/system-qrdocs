import html
import shutil
import tempfile
from pathlib import Path

from qrdocs.entries import Entry, load_entries


def _render_markdown_basic(text: str) -> str:
    """
    Minimal Markdown renderer for v0.1 development.

    Supports headings and plain paragraphs. This is intentionally small;
    richer Markdown/image handling can replace it later without changing
    the build interface.
    """
    output = []
    paragraph = []

    def flush_paragraph():
        if paragraph:
            content = " ".join(paragraph)
            output.append(f"<p>{html.escape(content)}</p>")
            paragraph.clear()

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            flush_paragraph()
            continue

        if line.startswith("### "):
            flush_paragraph()
            output.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            flush_paragraph()
            output.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            flush_paragraph()
            output.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("<!--"):
            # Ignore template comments for now.
            continue
        else:
            paragraph.append(line)

    flush_paragraph()
    return "\n".join(output)


def _page_document(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
</head>
<body>
    <main>
{body}
    </main>
</body>
</html>
"""


def _render_entry(entry: Entry) -> str:
    title = entry.title or entry.asset_id or "Untitled"
    body = _render_markdown_basic(entry.text)
    return _page_document(title, body)


def _render_index(entries: list[Entry]) -> str:
    items = []

    for entry in entries:
        asset_id = entry.asset_id or "(no asset id)"
        title = entry.title or "(untitled)"
        location = entry.current_location or "Unknown"

        filename = f"{entry.path.stem}.html"

        items.append(
            "<li>"
            f'<a href="{html.escape(filename)}">'
            f"{html.escape(asset_id)} - {html.escape(title)}"
            "</a>"
            f" — {html.escape(location)}"
            "</li>"
        )

    if items:
        listing = "<ul>\n" + "\n".join(items) + "\n</ul>"
    else:
        listing = "<p>No documentation entries found.</p>"

    body = f"""
<h1>SYSTEM-QRDOCS</h1>
<p>Private documentation index</p>
{listing}
"""

    return _page_document("SYSTEM-QRDOCS", body)


def build_private_site(data_dir: Path, output_dir: Path) -> int:
    """
    Build the private HTML site from canonical Markdown.

    The new site is generated in a temporary directory first. The existing
    output is only replaced after the complete build succeeds.
    """
    entries = load_entries(data_dir)

    output_dir = output_dir.resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix=f".{output_dir.name}-build-",
            dir=output_dir.parent,
        )
    )

    backup_dir = output_dir.with_name(f".{output_dir.name}-backup")

    try:
        for entry in entries:
            destination = temp_dir / f"{entry.path.stem}.html"
            destination.write_text(
                _render_entry(entry),
                encoding="utf-8",
            )

        (temp_dir / "index.html").write_text(
            _render_index(entries),
            encoding="utf-8",
        )

        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        if output_dir.exists():
            output_dir.rename(backup_dir)

        try:
            temp_dir.rename(output_dir)
        except Exception:
            if backup_dir.exists() and not output_dir.exists():
                backup_dir.rename(output_dir)
            raise

        if backup_dir.exists():
            shutil.rmtree(backup_dir)

    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    return len(entries)