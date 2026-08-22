from pathlib import Path
import tomllib


DEFAULT_CONFIG_PATH = Path("/etc/system-qrdocs/config.toml")


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    if not path.exists():
        return {}

    with path.open("rb") as file:
        return tomllib.load(file)


def get_public_base_url(config: dict) -> str | None:
    public = config.get("public", {})
    base_url = public.get("base_url")

    if not base_url:
        return None

    return str(base_url).rstrip("/")


def get_default_printer(config: dict) -> str | None:
    printing = config.get("printing", {})
    printer = printing.get("default_printer")

    if not printer:
        return None

    return str(printer)