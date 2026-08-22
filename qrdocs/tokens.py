import json
import secrets
from pathlib import Path


TOKEN_FILE = ".public-tokens.json"


def load_tokens(data_dir: Path) -> dict[str, str]:
    path = data_dir / TOKEN_FILE

    if not path.exists():
        return {}

    return json.loads(path.read_text(encoding="utf-8"))


def save_tokens(data_dir: Path, tokens: dict[str, str]) -> None:
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
    tokens = load_tokens(data_dir)
    key = asset_id.upper()

    if key in tokens:
        return tokens[key]

    token = secrets.token_urlsafe(24)
    tokens[key] = token
    save_tokens(data_dir, tokens)

    return token
