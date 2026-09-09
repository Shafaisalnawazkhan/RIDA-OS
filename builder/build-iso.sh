#!/usr/bin/env bash
set -eo pipefail

echo "=========================================================="
echo "          BUILDING RIDA OS 1.0 (SAPPHIRE EDITION)         "
echo "        Debian GNU/Linux 12 (Bookworm) + KDE Plasma       "
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
    echo "[-] Error: live-build must be executed with root privileges."
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE_BUILD_DIR="${PROJECT_ROOT}/live-build"
OUTPUT_DIR="${PROJECT_ROOT}/output"

mkdir -p "${OUTPUT_DIR}"
cd "${LIVE_BUILD_DIR}"

echo "[+] Step 1: Cleaning previous build artifacts..."
lb clean --purge || true

echo "[+] Step 2: Running auto/config..."
if [ -f "auto/config" ]; then
    chmod +x auto/config auto/clean auto/build || true
    ./auto/config
else
    echo "[-] Error: auto/config not found in ${LIVE_BUILD_DIR}"
    exit 1
fi

echo "[+] Step 3: Building Debian hybrid ISO image..."
echo "    This will download packages, bootstrap the rootfs, and package the ISO."
lb build 2>&1 | tee "${OUTPUT_DIR}/build.log"

echo "[+] Step 4: Finalizing release image..."
ISO_FILE=$(find . -maxdepth 1 -name "*.iso" | head -n 1)

if [ -n "${ISO_FILE}" ] && [ -f "${ISO_FILE}" ]; then
    FINAL_NAME="rida-os-1.0-amd64.iso"
    mv "${ISO_FILE}" "${OUTPUT_DIR}/${FINAL_NAME}"
    
    cd "${OUTPUT_DIR}"
    sha256sum "${FINAL_NAME}" > "${FINAL_NAME}.sha256"
    
    echo ""
    echo "=========================================================="
    echo "  SUCCESS! RIDA OS ISO image created successfully!"
    echo "  Location: ${OUTPUT_DIR}/${FINAL_NAME}"
    echo "  SHA256:   $(cat ${FINAL_NAME}.sha256)"
    echo "=========================================================="
else
    echo "[-] Build completed but no ISO was generated. Check ${OUTPUT_DIR}/build.log"
    exit 1
fi
