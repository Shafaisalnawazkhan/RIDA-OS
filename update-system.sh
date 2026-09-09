#!/usr/bin/env bash
set -e

# ==========================================================
#        RIDA OS Live & Installed System Updater
# ==========================================================
# Run inside RIDA OS to instantly pull the latest UI, themes,
# layouts, and apps directly from GitHub without reinstalling!

echo "=========================================================="
echo "          UPDATING RIDA OS DESKTOP & UI TOOLS             "
echo "=========================================================="

REPO_BASE="https://raw.githubusercontent.com/Shafaisalnawazkhan/RIDA-OS/main"
TARGET_DIR="/usr/share/rida"

if [ "$EUID" -ne 0 ]; then
    echo "[-] Please run as root or with sudo:"
    echo "    sudo bash update-system.sh"
    exit 1
fi

echo "[1/4] Updating RIDA Appearance & Layout Switcher..."
mkdir -p "${TARGET_DIR}/apps/rida-appearance/layouts"
curl -sSL "${REPO_BASE}/apps/rida-appearance/rida_appearance.py" -o "${TARGET_DIR}/apps/rida-appearance/rida_appearance.py"
curl -sSL "${REPO_BASE}/apps/rida-appearance/layouts/windows_classic.js" -o "${TARGET_DIR}/apps/rida-appearance/layouts/windows_classic.js"
curl -sSL "${REPO_BASE}/apps/rida-appearance/layouts/windows_modern.js" -o "${TARGET_DIR}/apps/rida-appearance/layouts/windows_modern.js"
curl -sSL "${REPO_BASE}/apps/rida-appearance/layouts/macos_dock.js" -o "${TARGET_DIR}/apps/rida-appearance/layouts/macos_dock.js"
curl -sSL "${REPO_BASE}/apps/rida-appearance/layouts/compact.js" -o "${TARGET_DIR}/apps/rida-appearance/layouts/compact.js"
chmod +x "${TARGET_DIR}/apps/rida-appearance/rida_appearance.py"

echo "[2/4] Updating RIDA Welcome Onboarding Wizard..."
mkdir -p "${TARGET_DIR}/apps/rida-welcome"
curl -sSL "${REPO_BASE}/apps/rida-welcome/rida_welcome.py" -o "${TARGET_DIR}/apps/rida-welcome/rida_welcome.py"
chmod +x "${TARGET_DIR}/apps/rida-welcome/rida_welcome.py"

echo "[3/5] Updating Wallpapers, Icons, and Splash Screen..."
mkdir -p "${TARGET_DIR}/wallpapers" "${TARGET_DIR}/icons"
curl -sSL "${REPO_BASE}/live-build/config/includes.chroot/usr/share/rida/wallpapers/rida-sapphire-dark.svg" -o "${TARGET_DIR}/wallpapers/rida-sapphire-dark.svg"
curl -sSL "${REPO_BASE}/live-build/config/includes.chroot/usr/share/rida/icons/rida-logo.svg" -o "${TARGET_DIR}/icons/rida-logo.svg"

# Install custom RIDA splash theme
mkdir -p /usr/share/plasma/look-and-feel/org.rida.desktop/contents/splash
curl -sSL "${REPO_BASE}/live-build/config/includes.chroot/usr/share/plasma/look-and-feel/org.rida.desktop/contents/splash/Splash.qml" -o /usr/share/plasma/look-and-feel/org.rida.desktop/contents/splash/Splash.qml
curl -sSL "${REPO_BASE}/live-build/config/includes.chroot/usr/share/plasma/look-and-feel/org.rida.desktop/metadata.desktop" -o /usr/share/plasma/look-and-feel/org.rida.desktop/metadata.desktop
kwriteconfig5 --file ksplashrc --group KSplash --key Theme org.rida.desktop 2>/dev/null || true
kwriteconfig5 --file ksplashrc --group KSplash --key Engine KSplashQML 2>/dev/null || true

echo "[4/5] Installing /usr/bin/rida-update command..."
cp "$0" /usr/bin/rida-update || true
chmod +x /usr/bin/rida-update || true

echo ""
echo "=========================================================="
echo " [OK] RIDA OS Updated Successfully!"
echo "      Close and relaunch 'RIDA Appearance' from your menu"
echo "      or dock to see the new modern UI!"
echo "=========================================================="
