#!/usr/bin/env bash
set -e

echo "=== RIDA OS WSL2 Build Environment ==="

# Check/Install prerequisites
echo "[+] Ensuring live-build and packaging tools are installed..."
apt-get update -qq
apt-get install -y -qq \
    live-build \
    debootstrap \
    xorriso \
    squashfs-tools \
    isolinux \
    syslinux-efi \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools \
    rsync

# Execute the core builder
chmod +x builder/build-iso.sh
./builder/build-iso.sh
