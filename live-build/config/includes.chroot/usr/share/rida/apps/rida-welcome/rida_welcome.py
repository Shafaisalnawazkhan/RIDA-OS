#!/usr/bin/env python3
"""
RIDA OS Welcome & Onboarding Wizard
Guided first-boot setup for new users: layout selection, hardware checks,
codecs & Flatpak activation, and curated software installation.
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

# Paths
HOME_DIR = Path.home()
AUTOSTART_DIR = HOME_DIR / ".config" / "autostart"
AUTOSTART_FILE = AUTOSTART_DIR / "rida-welcome.desktop"

def get_system_specs():
    """Detect basic system specs for user display."""
    specs = {
        "os": "RIDA OS 1.0 (Sapphire)",
        "kernel": platform.release(),
        "arch": platform.machine(),
        "cpu": "Unknown Processor",
        "memory": "Unknown RAM",
        "gpu": "Detecting...",
    }
    
    # Try reading Linux /proc/cpuinfo and /proc/meminfo
    if Path("/proc/cpuinfo").exists():
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        specs["cpu"] = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

    if Path("/proc/meminfo").exists():
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        kb = int(line.split()[1])
                        gb = round(kb / 1024 / 1024, 1)
                        specs["memory"] = f"{gb} GB"
                        break
        except Exception:
            pass

    # Try lspci for GPU
    try:
        res = subprocess.run(["lspci"], capture_output=True, text=True, timeout=2)
        for line in res.stdout.splitlines():
            if "VGA" in line or "3D" in line:
                specs["gpu"] = line.split(":", 2)[-1].strip()
                break
    except Exception:
        specs["gpu"] = "Standard Graphics Adapter"

    return specs

def toggle_autostart(enable: bool):
    """Enable or disable first-boot welcome screen."""
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    if enable:
        content = """[Desktop Entry]
Type=Application
Exec=python3 /usr/share/rida/apps/rida-welcome/rida_welcome.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=RIDA Welcome
"""
        with open(AUTOSTART_FILE, "w") as f:
            f.write(content)
    else:
        if AUTOSTART_FILE.exists():
            AUTOSTART_FILE.unlink()

def run_command_in_terminal(cmd: str, title: str = "RIDA Installer"):
    """Launches command in Konsole terminal with visual progress."""
    is_linux = sys.platform.startswith("linux")
    if is_linux:
        # Check konsole or x-terminal-emulator
        terminal = "konsole" if subprocess.run(["which", "konsole"], capture_output=True).returncode == 0 else "x-terminal-emulator"
        subprocess.Popen([terminal, "-e", "bash", "-c", f"echo '=== {title} ==='; {cmd}; echo 'Press enter to close'; read"])
    else:
        print(f"[Demo] Would run: {cmd}")

# Check Qt
QT_AVAILABLE = False
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QStackedWidget, QListWidget,
        QListWidgetItem, QCheckBox, QScrollArea, QGridLayout
    )
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtGui import QFont, QIcon
    QT_AVAILABLE = True
    QT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QPushButton, QFrame, QStackedWidget, QListWidget,
            QListWidgetItem, QCheckBox, QScrollArea, QGridLayout
        )
        from PyQt5.QtCore import Qt, QSize
        from PyQt5.QtGui import QFont, QIcon
        QT_AVAILABLE = True
        QT_VERSION = 5
    except ImportError:
        QT_AVAILABLE = False

if QT_AVAILABLE:
    class RidaWelcomeWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Welcome to RIDA OS")
            self.resize(860, 600)
            self.specs = get_system_specs()
            self._setup_ui()
            self._apply_styles()

        def _setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            root_layout = QHBoxLayout(central)
            root_layout.setContentsMargins(0, 0, 0, 0)
            root_layout.setSpacing(0)

            # Left Sidebar Navigation
            sidebar = QWidget()
            sidebar.setFixedWidth(240)
            sidebar.setObjectName("Sidebar")
            s_layout = QVBoxLayout(sidebar)
            s_layout.setContentsMargins(20, 24, 20, 20)
            s_layout.setSpacing(16)

            # Logo & Brand
            brand_box = QHBoxLayout()
            logo_icon = QLabel("RD")
            logo_icon.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2D7DFF, stop:1 #1E40AF);
                color: #FFFFFF;
                font-weight: 900;
                font-size: 16px;
                padding: 8px 12px;
                border-radius: 8px;
            """)
            brand_title = QVBoxLayout()
            b1 = QLabel("RIDA OS")
            b1.setStyleSheet("font-size: 17px; font-weight: 800; color: #FFFFFF;")
            b2 = QLabel("Debian • KDE Plasma")
            b2.setStyleSheet("font-size: 11px; color: #94A3B8;")
            brand_title.addWidget(b1)
            brand_title.addWidget(b2)
            brand_box.addWidget(logo_icon)
            brand_box.addLayout(brand_title)
            s_layout.addLayout(brand_box)
            s_layout.addSpacing(16)

            # Navigation list
            self.nav_list = QListWidget()
            self.nav_list.setObjectName("NavList")
            nav_items = [
                ("👋  Introduction", 0),
                ("🎨  Desktop Layout", 1),
                ("⚡  Drivers & Hardware", 2),
                ("📦  Codecs & Software", 3),
                ("💡  Tips & Shortcuts", 4),
            ]
            for title, idx in nav_items:
                item = QListWidgetItem(title)
                self.nav_list.addItem(item)

            self.nav_list.setCurrentRow(0)
            self.nav_list.currentRowChanged.connect(self._on_tab_changed)
            s_layout.addWidget(self.nav_list)
            s_layout.addStretch()

            # Autostart checkbox
            self.autostart_cb = QCheckBox("Show on system startup")
            self.autostart_cb.setChecked(AUTOSTART_FILE.exists() or True)
            self.autostart_cb.setStyleSheet("color: #94A3B8; font-size: 11px;")
            self.autostart_cb.toggled.connect(toggle_autostart)
            s_layout.addWidget(self.autostart_cb)

            root_layout.addWidget(sidebar)

            # Right Content Pages
            self.stack = QStackedWidget()
            self.stack.setObjectName("ContentStack")

            self.stack.addWidget(self._create_intro_page())
            self.stack.addWidget(self._create_layout_page())
            self.stack.addWidget(self._create_hardware_page())
            self.stack.addWidget(self._create_software_page())
            self.stack.addWidget(self._create_tips_page())

            root_layout.addWidget(self.stack)

        def _on_tab_changed(self, row):
            self.stack.setCurrentIndex(row)

        def _create_intro_page(self):
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(36, 36, 36, 36)
            v.setSpacing(18)

            h1 = QLabel("Welcome to your new operating system.")
            h1.setStyleSheet("font-size: 26px; font-weight: 800; color: #FFFFFF;")
            v.addWidget(h1)

            p1 = QLabel(
                "RIDA OS brings together the rock-solid reliability of Debian GNU/Linux "
                "with the fluid beauty and power of KDE Plasma. Crafted to be familiar, lightning-fast, "
                "and private out of the box."
            )
            p1.setWordWrap(True)
            p1.setStyleSheet("font-size: 14px; color: #94A3B8; line-height: 1.5;")
            v.addWidget(p1)

            # Specs Card
            specs_card = QFrame()
            specs_card.setStyleSheet("background: #181D26; border: 1px solid #283141; border-radius: 12px; padding: 18px;")
            sc_layout = QVBoxLayout(specs_card)
            
            sc_title = QLabel("System Information")
            sc_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2D7DFF;")
            sc_layout.addWidget(sc_title)

            grid = QGridLayout()
            grid.addWidget(QLabel("Operating System:"), 0, 0)
            grid.addWidget(QLabel(self.specs["os"]), 0, 1)
            grid.addWidget(QLabel("Linux Kernel:"), 1, 0)
            grid.addWidget(QLabel(self.specs["kernel"]), 1, 1)
            grid.addWidget(QLabel("Processor:"), 2, 0)
            grid.addWidget(QLabel(self.specs["cpu"]), 2, 1)
            grid.addWidget(QLabel("Installed Memory:"), 3, 0)
            grid.addWidget(QLabel(self.specs["memory"]), 3, 1)
            grid.addWidget(QLabel("Graphics:"), 4, 0)
            grid.addWidget(QLabel(self.specs["gpu"]), 4, 1)

            for i in range(grid.rowCount()):
                grid.itemAtPosition(i, 0).widget().setStyleSheet("color: #64748B; font-weight: 600; font-size: 12px;")
                grid.itemAtPosition(i, 1).widget().setStyleSheet("color: #E2E8F0; font-size: 12px;")

            sc_layout.addLayout(grid)
            v.addWidget(specs_card)
            v.addStretch()

            next_btn = QPushButton("Get Started →")
            next_btn.setObjectName("PrimaryBtn")
            next_btn.setFixedSize(140, 40)
            next_btn.clicked.connect(lambda: self.nav_list.setCurrentRow(1))
            v.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignRight if QT_VERSION == 6 else Qt.AlignRight)

            return w

        def _create_layout_page(self):
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(36, 36, 36, 36)
            v.setSpacing(16)

            h1 = QLabel("Choose Your Desktop Style")
            h1.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
            v.addWidget(h1)

            p1 = QLabel("Pick the layout that matches how you work best. You can change this at any time in RIDA Appearance.")
            p1.setWordWrap(True)
            p1.setStyleSheet("font-size: 13px; color: #94A3B8;")
            v.addWidget(p1)

            # Button to launch full RIDA Appearance
            app_btn = QPushButton("Open RIDA Appearance Tool")
            app_btn.setObjectName("PrimaryBtn")
            app_btn.setFixedHeight(42)
            app_btn.clicked.connect(self._launch_appearance)
            v.addWidget(app_btn)

            v.addStretch()
            return w

        def _create_hardware_page(self):
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(36, 36, 36, 36)
            v.setSpacing(16)

            h1 = QLabel("Hardware & Driver Diagnostics")
            h1.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
            v.addWidget(h1)

            info = QLabel(
                "RIDA OS includes non-free firmware for Intel, Realtek, Atheros, and Broadcom wireless adapters, "
                "as well as AMD and Nvidia graphics accelerators."
            )
            info.setWordWrap(True)
            info.setStyleSheet("font-size: 13px; color: #94A3B8;")
            v.addWidget(info)

            # Driver actions
            card = QFrame()
            card.setStyleSheet("background: #181D26; border: 1px solid #283141; border-radius: 12px; padding: 16px;")
            cv = QVBoxLayout(card)
            cv.setSpacing(12)

            chk_gpu = QPushButton("Detect & Install Proprietary Nvidia Drivers")
            chk_gpu.setStyleSheet("background: #252D3D; color: #E2E8F0; padding: 10px; border-radius: 8px; text-align: left;")
            chk_gpu.clicked.connect(lambda: run_command_in_terminal("sudo apt update && sudo apt install -y nvidia-detect && nvidia-detect", "Nvidia Detection"))
            cv.addWidget(chk_gpu)

            chk_wifi = QPushButton("Verify Wireless / Wi-Fi Firmware Status")
            chk_wifi.setStyleSheet("background: #252D3D; color: #E2E8F0; padding: 10px; border-radius: 8px; text-align: left;")
            chk_wifi.clicked.connect(lambda: run_command_in_terminal("sudo dmesg | grep -i firmware || echo 'All firmware loaded successfully!'", "Wi-Fi Firmware Check"))
            cv.addWidget(chk_wifi)

            v.addWidget(card)
            v.addStretch()
            return w

        def _create_software_page(self):
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(36, 36, 36, 36)
            v.setSpacing(16)

            h1 = QLabel("Essential Codecs & App Store")
            h1.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
            v.addWidget(h1)

            grid = QGridLayout()
            grid.setSpacing(12)

            apps = [
                ("Flatpak / Flathub", "Enable the vast universe of modern Linux sandbox apps", "flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo"),
                ("Multimedia Codecs", "Install extra video, audio, MP3, and AAC codecs", "sudo apt update && sudo apt install -y gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad ffmpeg"),
                ("Google Chrome", "Fast, modern web browser by Google", "flatpak install -y flathub com.google.Chrome"),
                ("Brave Browser", "Privacy-focused ad-blocking web browser", "flatpak install -y flathub com.brave.Browser"),
                ("LibreOffice Suite", "Complete office productivity suite (Docs, Sheets, Slides)", "sudo apt install -y libreoffice"),
                ("Visual Studio Code", "Code editor and development environment", "flatpak install -y flathub com.visualstudio.code"),
                ("Steam Gaming", "Digital gaming distribution platform", "flatpak install -y flathub com.valvesoftware.Steam"),
                ("VLC Media Player", "Play any video format with ease", "sudo apt install -y vlc"),
            ]

            for i, (name, desc, cmd) in enumerate(apps):
                f = QFrame()
                f.setStyleSheet("background: #181D26; border: 1px solid #283141; border-radius: 10px; padding: 12px;")
                fl = QVBoxLayout(f)
                fl.setSpacing(4)
                
                title = QLabel(name)
                title.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 13px;")
                fl.addWidget(title)

                sub = QLabel(desc)
                sub.setStyleSheet("color: #94A3B8; font-size: 11px;")
                fl.addWidget(sub)

                btn = QPushButton("Install")
                btn.setStyleSheet("background: #2D7DFF; color: white; border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: bold;")
                btn.clicked.connect(lambda _, c=cmd, n=name: run_command_in_terminal(c, f"Installing {n}"))
                fl.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight if QT_VERSION == 6 else Qt.AlignRight)

                grid.addWidget(f, i // 2, i % 2)

            scroll = QScrollArea()
            scroll_widget = QWidget()
            scroll_widget.setLayout(grid)
            scroll.setWidget(scroll_widget)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("border: none; background: transparent;")
            v.addWidget(scroll)
            return w

        def _create_tips_page(self):
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(36, 36, 36, 36)
            v.setSpacing(16)

            h1 = QLabel("Useful Tips & Shortcuts")
            h1.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
            v.addWidget(h1)

            tips = [
                ("Super (Windows) Key", "Open the Application Start Menu"),
                ("Alt + Space", "Open KRunner search bar (find apps, files, perform calculations)"),
                ("Super + E", "Open Dolphin File Manager"),
                ("Ctrl + Alt + T", "Open Konsole Terminal"),
                ("Super + Tab", "Switch between open windows and virtual desktops"),
                ("Print Screen", "Take full or regional screenshot using Spectacle"),
            ]

            card = QFrame()
            card.setStyleSheet("background: #181D26; border: 1px solid #283141; border-radius: 12px; padding: 18px;")
            cv = QVBoxLayout(card)
            cv.setSpacing(12)

            for key, desc in tips:
                row = QHBoxLayout()
                badge = QLabel(key)
                badge.setStyleSheet("background: #252D3D; color: #2D7DFF; font-weight: bold; padding: 6px 12px; border-radius: 6px; font-size: 12px;")
                txt = QLabel(desc)
                txt.setStyleSheet("color: #E2E8F0; font-size: 13px;")
                row.addWidget(badge)
                row.addWidget(txt)
                row.addStretch()
                cv.addLayout(row)

            v.addWidget(card)
            v.addStretch()

            done_btn = QPushButton("Finish Setup")
            done_btn.setObjectName("PrimaryBtn")
            done_btn.setFixedSize(140, 40)
            done_btn.clicked.connect(self.close)
            v.addWidget(done_btn, alignment=Qt.AlignmentFlag.AlignRight if QT_VERSION == 6 else Qt.AlignRight)
            return w

        def _launch_appearance(self):
            appearance_script = Path("/usr/share/rida/apps/rida-appearance/rida_appearance.py")
            if not appearance_script.exists():
                appearance_script = Path(__file__).parent.parent / "rida-appearance" / "rida_appearance.py"
            
            if appearance_script.exists():
                subprocess.Popen([sys.executable, str(appearance_script)])
            else:
                print(f"Could not locate appearance script at {appearance_script}")

        def _apply_styles(self):
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #0F1218;
                }
                QWidget#Sidebar {
                    background-color: #141820;
                    border-right: 1px solid #202632;
                }
                QListWidget#NavList {
                    background: transparent;
                    border: none;
                    outline: none;
                }
                QListWidget#NavList::item {
                    color: #94A3B8;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 12px 14px;
                    border-radius: 8px;
                    margin-bottom: 4px;
                }
                QListWidget#NavList::item:selected {
                    background-color: #1E293B;
                    color: #2D7DFF;
                }
                QListWidget#NavList::item:hover {
                    color: #FFFFFF;
                    background-color: #18202F;
                }
                QPushButton#PrimaryBtn {
                    background-color: #2D7DFF;
                    color: #FFFFFF;
                    font-weight: bold;
                    border-radius: 8px;
                    border: none;
                    padding: 8px 16px;
                }
                QPushButton#PrimaryBtn:hover {
                    background-color: #1D6AE5;
                }
            """)

else:
    # Tkinter fallback for non-Qt environments
    import tkinter as tk
    from tkinter import messagebox

    class RidaWelcomeWindow:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Welcome to RIDA OS (Demo Mode)")
            self.root.geometry("640x480")
            self.root.configure(bg="#0F1218")
            lbl = tk.Label(self.root, text="Welcome to RIDA OS", font=("Helvetica", 20, "bold"), fg="#FFFFFF", bg="#0F1218")
            lbl.pack(pady=20)
            sub = tk.Label(self.root, text="Debian Reliability + Modern Elegance", font=("Helvetica", 12), fg="#94A3B8", bg="#0F1218")
            sub.pack(pady=5)
            btn = tk.Button(self.root, text="Launch Appearance Tool", command=lambda: messagebox.showinfo("RIDA", "Opening appearance..."),
                            bg="#2D7DFF", fg="#FFFFFF", font=("Helvetica", 12, "bold"), padx=15, pady=8)
            btn.pack(pady=30)

        def show(self):
            self.root.mainloop()

def main():
    if QT_AVAILABLE:
        app = QApplication(sys.argv)
        app.setApplicationName("RIDA Welcome")
        win = RidaWelcomeWindow()
        win.show()
        sys.exit(app.exec())
    else:
        win = RidaWelcomeWindow()
        win.show()

if __name__ == "__main__":
    main()
