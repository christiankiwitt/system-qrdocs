#!/usr/bin/env bash
set -euo pipefail

APP_NAME="qrdocs"
INSTALL_DIR="/opt/qrdocs"
VENV_DIR="${INSTALL_DIR}/venv"
CONFIG_DIR="/etc/system-qrdocs"
CONFIG_FILE="${CONFIG_DIR}/config.toml"
DATA_DIR="/var/lib/system-qrdocs"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Error: install.sh must be run as root."
    echo "Run: sudo ./install.sh"
    exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing QRDOCS..."

echo "Checking required commands..."

for command in python3; do
    if ! command -v "${command}" >/dev/null 2>&1; then
        echo "Error: required command not found: ${command}"
        exit 1
    fi
done

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "Error: Python venv support is not available."
    echo "On Debian/Ubuntu, install it with:"
    echo "  sudo apt install python3-venv"
    exit 1
fi

echo "Creating installation directory..."
mkdir -p "${INSTALL_DIR}"

echo "Creating Python virtual environment..."
if [[ ! -d "${VENV_DIR}" ]]; then
    python3 -m venv "${VENV_DIR}"
fi

echo "Installing QRDOCS Python package..."
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install --upgrade "${SCRIPT_DIR}"

echo "Installing qrdocs command..."
ln -sfn "${VENV_DIR}/bin/qrdocs" /usr/local/bin/qrdocs

echo "Creating configuration directory..."
mkdir -p "${CONFIG_DIR}"

if [[ ! -f "${CONFIG_FILE}" ]]; then
    if [[ -f "${SCRIPT_DIR}/examples/config.toml" ]]; then
        cp "${SCRIPT_DIR}/examples/config.toml" "${CONFIG_FILE}"
        chmod 0644 "${CONFIG_FILE}"
        echo "Installed example configuration:"
        echo "  ${CONFIG_FILE}"
    else
        echo "Warning: examples/config.toml was not found."
        echo "Configuration file was not created."
    fi
else
    echo "Existing configuration preserved:"
    echo "  ${CONFIG_FILE}"
fi

echo "Creating persistent data directories..."
mkdir -p \
    "${DATA_DIR}" \
    "${DATA_DIR}/images" \
    "${DATA_DIR}/public" \
    "${DATA_DIR}/public/images"

echo
echo "QRDOCS installation complete."
echo
echo "Command:"
echo "  qrdocs"
echo
echo "Configuration:"
echo "  ${CONFIG_FILE}"
echo
echo "Persistent data:"
echo "  ${DATA_DIR}"
echo
echo "Existing configuration and persistent data are never overwritten by this installer."
echo
echo "Next steps:"
echo "  1. Review ${CONFIG_FILE}"
echo "  2. Configure networking/web serving as described in README.md"
echo "  3. Configure CUPS if label printing is required"
echo "  4. Run: qrdocs --help"