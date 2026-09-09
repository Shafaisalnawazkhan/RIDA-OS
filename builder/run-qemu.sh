#!/usr/bin/env bash
# Quick QEMU launcher to test RIDA OS ISO image
ISO_PATH="${1:-output/rida-os-1.0-amd64.iso}"

if [ ! -f "${ISO_PATH}" ]; then
    echo "[-] ISO image not found at ${ISO_PATH}"
    echo "    Usage: $0 [path/to/rida-os.iso]"
    exit 1
fi

echo "[*] Launching RIDA OS in QEMU..."

# Determine acceleration
ACCEL=""
if [ -e /dev/kvm ] && [ -w /dev/kvm ]; then
    ACCEL="-enable-kvm -cpu host"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    ACCEL="-accel hvf -cpu host"
fi

qemu-system-x86_64 \
    ${ACCEL} \
    -m 4096 \
    -smp 4 \
    -vga virtio \
    -display default,show-cursor=on \
    -cdrom "${ISO_PATH}" \
    -boot d \
    -net nic -net user
