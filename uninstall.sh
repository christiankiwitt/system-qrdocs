#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/opt/qrdocs"
COMMAND_LINK="/usr/local/bin/qrdocs"
CONFIG_DIR="/etc/system-qrdocs"
DATA_DIR="/var/lib/system-qrdocs"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Error: uninstall.sh must be run as root."
    echo "Run: sudo ./uninstall.sh"
    exit 1
fi

echo "Uninstalling QRDOCS..."

if [[ -L "${COMMAND_LINK}" || -e "${COMMAND_LINK}" ]]; then
    rm -f "${COMMAND_LINK}"
    echo "Removed command:"
    echo "  ${COMMAND_LINK}"
fi

if [[ -d "${INSTALL_DIR}" ]]; then
    rm -rf "${INSTALL_DIR}"
    echo "Removed application files:"
    echo "  ${INSTALL_DIR}"
fi

echo
echo "QRDOCS application files have been removed."
echo
echo "The following were preserved:"
echo "  Configuration: ${CONFIG_DIR}"
echo "  Persistent data: ${DATA_DIR}"
echo
echo "To remove them manually as well:"
echo "  sudo rm -rf ${CONFIG_DIR}"
echo "  sudo rm -rf ${DATA_DIR}"