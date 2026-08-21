import html
import json
import secrets
import shutil
import tempfile
from pathlib import Path

from qrdocs.build import _page_document, _render_markdown_basic


TOKEN_FILE = ".public-tokens.json"


def _load_tokens(data_dir: Path) -> dict[str, str]:
    path = data_dir / TOKEN_FILE

    if not path.exists():
        return {}

    return json.loads(path.read_text(encoding="utf-8"))


def _save_tokens(data_dir: Path, tokens: dict[str, str]) -> None:
    path = data_dir / TOKEN_FILE
    temp_path = path.with_suffix(".tmp")

    temp_path.write_text(
        json.dumps(tokens, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    temp_path.replace(path)


def get_or_create_public_token(
    data_dir: Path,
    asset_id: str,
) -> str:
    tokens = _load_tokens(data_dir)
    key = asset_id.upper()

    if key in tokens:
        return tokens[key]

    token = secrets.token_urlsafe(24)
    tokens[key] = token
    _save_tokens(data_dir, tokens)

    return token


def public_source_path(
    data_dir: Path,
    asset_id: str,
) -> Path | None:
    public_dir = data_dir / "public"

    html_path = public_dir / f"{asset_id}.html"
    markdown_path = public_dir / f"{asset_id}.md"

    if html_path.exists():
        return html_path

    if markdown_path.exists():
        return markdown_path

    return None


def render_public_source(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    if path.suffix.casefold() == ".html":
        return text

    body = _render_markdown_basic(text)

    title = path.stem
    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break

    return _page_document(title, body)


def build_public_asset(
    *,
    data_dir: Path,
    asset_id: str,
    output_dir: Path,
) -> Path:
    source = public_source_path(data_dir, asset_id)

    if source is None:
        raise FileNotFoundError(
            f"No public Markdown or HTML source found for {asset_id}"
        )

    token = get_or_create_public_token(data_dir, asset_id)

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    live_dir = output_dir / "q" / token
    live_dir.parent.mkdir(parents=True, exist_ok=True)

    staging_dir = Path(
        tempfile.mkdtemp(
            prefix=f".{token}-build-",
            dir=live_dir.parent,
        )
    )

    backup_dir = live_dir.with_name(f".{token}-backup")

    try:
        page = render_public_source(source)

        index_path = staging_dir / "index.html"
        index_path.write_text(page, encoding="utf-8")
        index_path.chmod(0o644)

        public_images_dir = data_dir / "public" / "images"
        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
        }

        if public_images_dir.exists():
            matching_images = [
                path
                for path in public_images_dir.iterdir()
                if path.is_file()
                and path.stem.casefold() == asset_id.casefold()
                and path.suffix.casefold() in allowed_extensions
            ]

            if matching_images:
                destination_images_dir = staging_dir / "images"
                destination_images_dir.mkdir(parents=True, exist_ok=True)

                for image_path in matching_images:
                    shutil.copy2(
                        image_path,
                        destination_images_dir / image_path.name,
                    )

        staging_dir.chmod(0o755)

        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        if live_dir.exists():
            live_dir.rename(backup_dir)

        try:
            staging_dir.rename(live_dir)
            live_dir.chmod(0o755)
        except Exception:
            if backup_dir.exists() and not live_dir.exists():
                backup_dir.rename(live_dir)
            raise

        if backup_dir.exists():
            shutil.rmtree(backup_dir)

    finally:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)

    return live_dir / "index.html"


def public_url_path(
    data_dir: Path,
    asset_id: str,
) -> str:
    token = get_or_create_public_token(data_dir, asset_id)
    return f"/q/{token}/"