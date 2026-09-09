# RIDA OS (RD) 1.0 — Sapphire Edition

> **Debian's rock-solid stability meets modern, fluid elegance.**  
> A custom Linux distribution built on Debian 12 (Bookworm) and KDE Plasma, designed to deliver the approachable, polished experience of Zorin OS with the lightweight reliability of Debian.

---

## 🌟 Key Highlights

- **Debian 12 (Bookworm) Base:** Long-term stability, vast APT repositories, low overhead, and privacy-respecting foundation.
- **KDE Plasma 5.27 LTS Desktop:** Modern, fluid animations, fractional scaling, and high-DPI display readiness.
- **RIDA Appearance (Layout Switcher):** One-click layout switching between:
  - **Windows Standard:** Familiar bottom taskbar with left Start menu, pinned icons, and system tray.
  - **Windows Modern:** Centered taskbar with floating panel aesthetic.
  - **Cupertino (macOS):** Clean top menu/status bar with a floating bottom application dock.
  - **Compact / Minimalist:** High screen real-estate top panel for power users and laptops.
- **RIDA Welcome (First-Boot Onboarding):** Interactive setup wizard covering layout selection, hardware/Wi-Fi driver diagnostics, one-click multimedia codecs (`restricted-extras`), and popular software installs.
- **Out-of-the-Box Hardware Support:** Pre-loaded non-free firmware for Intel, Realtek, Atheros, and Broadcom wireless adapters, plus AMD and Nvidia GPU acceleration.
- **Modern App Ecosystem:** Flatpak and the Flathub catalog pre-integrated with KDE Discover for graphical, app-store style package management.
- **Calamares Graphical Installer:** Clean, modern installation wizard with guided partitioning, user creation, and slide tour.

---

## 📁 Repository Structure

```text
rida-os/
├── .github/workflows/build-iso.yml     # Automated cloud ISO builds via GitHub Actions
├── apps/                               # Custom RIDA Companion Utilities
│   ├── rida-appearance/                # Layout switcher (PyQt6 / KDE Plasma DBus)
│   │   ├── layouts/                    # Plasma JS layout definitions
│   │   ├── rida_appearance.py          # Main application
│   │   └── rida-appearance.desktop     # Desktop launcher
│   └── rida-welcome/                   # First-boot onboarding wizard
│       ├── rida_welcome.py             # Main onboarding app
│       └── rida-welcome.desktop        # Desktop launcher
├── builder/                            # Container & Automation Tools
│   ├── Dockerfile.builder              # Debian Bookworm container for live-build
│   ├── build-iso.sh                    # Core compilation script (lb clean/config/build)
│   ├── build-wsl.sh                    # WSL helper script
│   └── run-qemu.sh                     # QEMU emulator launch script
├── live-build/                         # Official Debian live-build recipe
│   ├── auto/                           # Clean, config, and build hooks
│   └── config/
│       ├── package-lists/              # Base, firmware, KDE, apps, installer
│       ├── hooks/live/                 # Flatpak, branding, Plymouth, Calamares setup
│       └── includes.chroot/            # Rootfs overlay (os-release, configs, assets)
├── build.bat                           # 1-Click Windows Docker Runner
├── build-wsl.bat                       # 1-Click Windows WSL2 Runner
└── README.md
```

---

## 🚀 How to Build the ISO

Because Debian live ISO creation requires Linux kernel privileges (`chroot`, loop mounts, `debootstrap`, and `xorriso`), you can build the ISO using any of the following methods:

### Option 1: 1-Click Windows Docker Build (Recommended)
1. Ensure **Docker Desktop** is running on your Windows machine.
2. Double-click `build.bat` (or run `./build.bat` in Command Prompt / PowerShell).
3. The build container will compile the hybrid ISO into `output/rida-os-1.0-amd64.iso`.

### Option 2: 1-Click Windows WSL2 Build
1. Open PowerShell and run:
   ```cmd
   build-wsl.bat
   ```
2. The script will install the necessary build dependencies inside your WSL Ubuntu/Debian distro and output the ISO to `output/`.

### Option 3: GitHub Actions (Free Cloud Build)
1. Push this repository to GitHub.
2. Go to the **Actions** tab in your repository and select **Build RIDA OS ISO**.
3. Click **Run workflow**. Once finished, download the ready-to-flash ISO directly from GitHub Artifacts!

### Option 4: Native Linux / Debian VM
Run inside any Debian/Ubuntu machine:
```bash
sudo apt-get install -y live-build debootstrap xorriso squashfs-tools isolinux syslinux-efi grub-pc-bin grub-efi-amd64-bin mtools dosfstools rsync
chmod +x builder/build-iso.sh
sudo ./builder/build-iso.sh
```

---

## 🧪 Testing the Generated ISO

### Launch with QEMU
```bash
./builder/run-qemu.sh output/rida-os-1.0-amd64.iso
```

### Launch in VirtualBox or VMware
1. Create a new 64-bit Linux virtual machine (Debian 64-bit).
2. Allocate at least 4 GB of RAM and 20 GB of virtual storage.
3. Attach `output/rida-os-1.0-amd64.iso` to the virtual optical drive and power on.

---

## 🛠️ Testing the Companion Tools Directly (on Windows/Linux)

You can launch and test the custom GUI tools directly using Python:

```bash
# Test RIDA Appearance (Desktop layout switcher)
python apps/rida-appearance/rida_appearance.py

# Test RIDA Welcome (First-boot onboarding wizard)
python apps/rida-welcome/rida_welcome.py
```

---

## 📋 Release Checklist

- [x] Dual BIOS and UEFI boot support (`grub-efi-amd64` + `syslinux-efi` + `grub-pc-bin`).
- [x] Non-free wireless firmware bundled (`firmware-iwlwifi`, `firmware-realtek`, `firmware-atheros`, `firmware-brcm80211`).
- [x] Proprietary graphics acceleration drivers pre-configured.
- [x] Calamares installer pre-seeded on desktop and live menu.
- [x] Custom Plymouth splash theme (`rida-pulse`) and GRUB theme.
- [x] Flathub repository enabled for Discover app store.
- [x] RIDA Appearance and RIDA Welcome companion apps integrated into autostart and desktop menus.

---

## 📜 License & Credits

- Base system: Debian GNU/Linux (SPI / Debian Project).
- Desktop Environment: KDE Plasma & KDE Frameworks.
- Installer: Calamares Project.
- RIDA OS design, branding, and companion tools: RIDA OS Project.
