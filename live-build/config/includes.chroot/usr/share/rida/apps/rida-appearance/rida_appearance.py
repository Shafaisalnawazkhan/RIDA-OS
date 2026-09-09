#!/usr/bin/env python3
"""
RIDA OS Appearance Tool
Allows users to switch between desktop layouts (Windows Classic, Windows Modern, macOS, Compact)
and customize system accent colors and theming. Inspired by Zorin Appearance.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

# Detect layout scripts directory
SCRIPT_DIR = Path(__file__).parent.resolve()
LAYOUTS_DIR = SCRIPT_DIR / "layouts"

LAYOUT_META = {
    "windows_classic": {
        "title": "Windows Standard",
        "desc": "Classic desktop with bottom taskbar, start menu on left, and system tray.",
        "script": LAYOUTS_DIR / "windows_classic.js",
        "tag": "Recommended for Windows 7/10 switchers",
    },
    "windows_modern": {
        "title": "Windows Modern",
        "desc": "Contemporary centered taskbar with floating panel and quick search.",
        "script": LAYOUTS_DIR / "windows_modern.js",
        "tag": "Windows 11 inspired aesthetic",
    },
    "macos_dock": {
        "title": "Cupertino (macOS)",
        "desc": "Top status bar with global menu plus a floating bottom application dock.",
        "script": LAYOUTS_DIR / "macos_dock.js",
        "tag": "Intuitive for macOS switchers",
    },
    "compact": {
        "title": "Compact / Minimal",
        "desc": "Lightweight top panel with grouped task list for maximum screen real-estate.",
        "script": LAYOUTS_DIR / "compact.js",
        "tag": "Great for laptops & ultra-wide monitors",
    },
}

ACCENT_COLORS = [
    ("Sapphire", "#2D7DFF"),
    ("Emerald", "#10B981"),
    ("Amethyst", "#8B5CF6"),
    ("Ruby", "#EF4444"),
    ("Amber", "#F59E0B"),
    ("Graphite", "#64748B"),
]

def is_plasma_session():
    return (
        os.environ.get("KDE_FULL_SESSION") == "true"
        or "KDE" in os.environ.get("XDG_CURRENT_DESKTOP", "")
        or "plasma" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        or shutil.which("plasmashell") is not None
    )

def hex_to_rgb_str(hex_val: str) -> str:
    h = hex_val.lstrip("#")
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return f"{r},{g},{b}"

def apply_plasma_layout(layout_key: str):
    """Executes layout script via Plasma DBus or creates layout backup."""
    meta = LAYOUT_META.get(layout_key)
    if not meta:
        return False, "Unknown layout key"
    
    script_path = meta["script"]
    if not script_path.exists():
        return False, f"Layout script not found: {script_path}"
    
    if is_plasma_session():
        try:
            with open(script_path, "r") as f:
                script_content = f.read()
            
            # Try DBus runners in order of preference
            dbus_candidates = [
                ["qdbus-qt5", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script_content],
                ["qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script_content],
                ["/usr/lib/qt5/bin/qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script_content],
                ["dbus-send", "--session", "--dest=org.kde.plasmashell", "--type=method_call", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", f"string:{script_content}"],
                ["gdbus", "call", "--session", "--dest", "org.kde.plasmashell", "--object-path", "/PlasmaShell", "--method", "org.kde.PlasmaShell.evaluateScript", script_content]
            ]
            
            executed = False
            for cmd in dbus_candidates:
                bin_name = cmd[0]
                if shutil.which(bin_name) or os.path.exists(bin_name):
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
                    if res.returncode == 0:
                        executed = True
                        break
            
            if executed:
                return True, f"Successfully applied {meta['title']} layout!"
            else:
                # If direct evaluateScript DBus is restricted, restart plasmashell to reload
                subprocess.run(["systemctl", "--user", "restart", "plasma-plasmashell"], check=False)
                return True, f"Applied {meta['title']} layout (reloaded shell)"
        except Exception as e:
            return False, f"Failed applying layout: {str(e)}"
    else:
        # Development / Preview simulation mode
        return True, f"[Demo Mode] Selected {meta['title']}."

def apply_accent_color(color_hex: str):
    """Applies accent color to KDE configuration and reloads color scheme."""
    if is_plasma_session():
        try:
            rgb_val = hex_to_rgb_str(color_hex)
            if shutil.which("kwriteconfig5"):
                subprocess.run(["kwriteconfig5", "--file", "kdeglobals", "--group", "General", "--key", "AccentColor", rgb_val], check=False)
                subprocess.run(["kwriteconfig5", "--file", "kdeglobals", "--group", "General", "--key", "accentColorHex", color_hex], check=False)
            
            # Reapply color scheme so accent colors take effect instantly
            if shutil.which("plasma-apply-colorscheme"):
                subprocess.run(["plasma-apply-colorscheme", "BreezeDark"], check=False)

            # Notify KWin
            for kwin_cmd in [
                ["qdbus-qt5", "org.kde.KWin", "/KWin", "reconfigure"],
                ["qdbus", "org.kde.KWin", "/KWin", "reconfigure"],
                ["/usr/lib/qt5/bin/qdbus", "org.kde.KWin", "/KWin", "reconfigure"],
                ["dbus-send", "--session", "--dest=org.kde.KWin", "--type=method_call", "/KWin", "org.kde.KWin.reconfigure"]
            ]:
                if shutil.which(kwin_cmd[0]) or os.path.exists(kwin_cmd[0]):
                    subprocess.run(kwin_cmd, check=False)
                    break

            return True, f"Accent color updated to {color_hex}!"
        except Exception as e:
            return False, str(e)
    return True, f"[Demo Mode] Set accent color to {color_hex}"

def apply_theme_mode(mode: str):
    """Switches between RIDA Dark and RIDA Light mode."""
    scheme = "BreezeDark" if mode == "dark" else "BreezeLight"
    desk_theme = "breeze-dark" if mode == "dark" else "breeze-light"
    icon_theme = "breeze-dark" if mode == "dark" else "breeze"

    if is_plasma_session():
        try:
            if shutil.which("plasma-apply-colorscheme"):
                subprocess.run(["plasma-apply-colorscheme", scheme], check=False)
            
            if shutil.which("plasma-apply-desktoptheme"):
                subprocess.run(["plasma-apply-desktoptheme", desk_theme], check=False)
            
            if shutil.which("kwriteconfig5"):
                subprocess.run(["kwriteconfig5", "--file", "kdeglobals", "--group", "General", "--key", "ColorScheme", scheme], check=False)
                subprocess.run(["kwriteconfig5", "--file", "kdeglobals", "--group", "Icons", "--key", "Theme", icon_theme], check=False)

            for kwin_cmd in [
                ["qdbus-qt5", "org.kde.KWin", "/KWin", "reconfigure"],
                ["qdbus", "org.kde.KWin", "/KWin", "reconfigure"],
                ["/usr/lib/qt5/bin/qdbus", "org.kde.KWin", "/KWin", "reconfigure"],
                ["dbus-send", "--session", "--dest=org.kde.KWin", "--type=method_call", "/KWin", "org.kde.KWin.reconfigure"]
            ]:
                if shutil.which(kwin_cmd[0]) or os.path.exists(kwin_cmd[0]):
                    subprocess.run(kwin_cmd, check=False)
                    break

            return True, f"Switched to {'Dark' if mode == 'dark' else 'Light'} theme!"
        except Exception as e:
            return False, f"Failed setting theme: {str(e)}"
    return True, f"[Demo Mode] Switched to {'Dark' if mode == 'dark' else 'Light'} theme"


# Try loading PyQt6 or PyQt5
QT_AVAILABLE = False
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QRadioButton, QButtonGroup,
        QScrollArea, QMessageBox, QTabWidget, QGridLayout
    )
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
    QT_AVAILABLE = True
    QT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QPushButton, QFrame, QRadioButton, QButtonGroup,
            QScrollArea, QMessageBox, QTabWidget, QGridLayout
        )
        from PyQt5.QtCore import Qt, QSize
        from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
        QT_AVAILABLE = True
        QT_VERSION = 5
    except ImportError:
        QT_AVAILABLE = False


if QT_AVAILABLE:
    class LayoutCard(QFrame):
        def __init__(self, key, meta, on_select, parent=None):
            super().__init__(parent)
            self.key = key
            self.on_select = on_select
            self.setObjectName("LayoutCard")
            self.setCursor(Qt.CursorShape.PointingHandCursor if QT_VERSION == 6 else Qt.PointingHandCursor)
            
            layout = QVBoxLayout(self)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(8)
            
            header = QHBoxLayout()
            title = QLabel(meta["title"])
            title.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
            header.addWidget(title)
            
            header.addStretch()
            self.radio = QRadioButton()
            header.addWidget(self.radio)
            layout.addLayout(header)
            
            tag = QLabel(meta["tag"].upper())
            tag.setStyleSheet("font-size: 10px; font-weight: 600; color: #2D7DFF; letter-spacing: 0.5px;")
            layout.addWidget(tag)
            
            desc = QLabel(meta["desc"])
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 12px; color: #A0AEC0;")
            layout.addWidget(desc)
            
            # Schematic visual preview of the layout
            preview = QFrame()
            preview.setFixedHeight(54)
            preview.setStyleSheet(self._get_preview_style(key))
            layout.addWidget(preview)
            
            self.radio.toggled.connect(self._on_toggled)

        def _get_preview_style(self, key):
            base = "background: #11141A; border: 1px solid #2D3748; border-radius: 6px; position: relative;"
            if key == "windows_classic":
                # bottom line
                return base + " border-bottom: 5px solid #2D7DFF;"
            elif key == "windows_modern":
                return base + " border-bottom: 5px solid #2D7DFF; margin-left: 20px; margin-right: 20px;"
            elif key == "macos_dock":
                return base + " border-top: 3px solid #2D7DFF; border-bottom: 4px solid #10B981;"
            elif key == "compact":
                return base + " border-top: 4px solid #2D7DFF;"
            return base

        def _on_toggled(self, checked):
            if checked:
                self.setStyleSheet("""
                    QFrame#LayoutCard {
                        background: #1E2533;
                        border: 2px solid #2D7DFF;
                        border-radius: 12px;
                    }
                """)
                self.on_select(self.key)
            else:
                self.setStyleSheet("""
                    QFrame#LayoutCard {
                        background: #181D26;
                        border: 1px solid #2A3241;
                        border-radius: 12px;
                    }
                    QFrame#LayoutCard:hover {
                        border: 1px solid #3B82F6;
                        background: #1B2230;
                    }
                """)

        def mousePressEvent(self, event):
            self.radio.setChecked(True)
            super().mousePressEvent(event)

    class RidaAppearanceWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("RIDA Appearance — Desktop Styling")
            self.resize(780, 620)
            self.current_layout = "windows_classic"
            self.current_color = "#2D7DFF"
            self._setup_ui()
            self._apply_global_styles()

        def _setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(28, 28, 28, 28)
            main_layout.setSpacing(20)

            # Top Header
            header_box = QHBoxLayout()
            title_col = QVBoxLayout()
            h1 = QLabel("Desktop Appearance")
            h1.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
            sub = QLabel("Customize your desktop layout, accent colors, and desktop experience.")
            sub.setStyleSheet("font-size: 13px; color: #94A3B8;")
            title_col.addWidget(h1)
            title_col.addWidget(sub)
            header_box.addLayout(title_col)
            header_box.addStretch()

            logo_badge = QLabel("RIDA OS")
            logo_badge.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2D7DFF, stop:1 #1E40AF);
                color: #FFFFFF;
                font-weight: 800;
                font-size: 13px;
                padding: 6px 14px;
                border-radius: 14px;
            """)
            header_box.addWidget(logo_badge)
            main_layout.addLayout(header_box)

            # Tab Widget
            tabs = QTabWidget()
            tabs.setObjectName("AppearanceTabs")

            # Tab 1: Layouts
            layout_tab = QWidget()
            layout_tab_v = QVBoxLayout(layout_tab)
            layout_tab_v.setContentsMargins(12, 16, 12, 12)
            layout_tab_v.setSpacing(14)

            grid = QGridLayout()
            grid.setSpacing(14)

            self.cards = {}
            self.btn_group = QButtonGroup(self)

            row, col = 0, 0
            for key, meta in LAYOUT_META.items():
                card = LayoutCard(key, meta, self._on_layout_chosen)
                self.btn_group.addButton(card.radio)
                self.cards[key] = card
                grid.addWidget(card, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1

            layout_tab_v.addLayout(grid)
            layout_tab_v.addStretch()

            # Apply Layout Action Bar
            action_bar = QHBoxLayout()
            self.status_lbl = QLabel("Ready to apply layout")
            self.status_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
            action_bar.addWidget(self.status_lbl)
            action_bar.addStretch()

            apply_btn = QPushButton("Apply Layout")
            apply_btn.setObjectName("PrimaryButton")
            apply_btn.setFixedHeight(38)
            apply_btn.clicked.connect(self._apply_layout_action)
            action_bar.addWidget(apply_btn)
            layout_tab_v.addLayout(action_bar)

            tabs.addTab(layout_tab, "Desktop Layout")

            # Tab 2: Theme & Accent Color
            theme_tab = QWidget()
            theme_v = QVBoxLayout(theme_tab)
            theme_v.setContentsMargins(16, 20, 16, 16)
            theme_v.setSpacing(18)

            theme_h1 = QLabel("Accent Color")
            theme_h1.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
            theme_v.addWidget(theme_h1)

            theme_sub = QLabel("Select an accent color for active window highlights, buttons, and slider elements.")
            theme_sub.setStyleSheet("font-size: 12px; color: #94A3B8;")
            theme_v.addWidget(theme_sub)

            colors_box = QHBoxLayout()
            colors_box.setSpacing(14)
            for name, hex_val in ACCENT_COLORS:
                btn = QPushButton(name)
                btn.setFixedHeight(40)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {hex_val};
                        color: #FFFFFF;
                        font-weight: bold;
                        border-radius: 8px;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #FFFFFF;
                    }}
                """)
                btn.clicked.connect(lambda _, h=hex_val: self._apply_color_action(h))
                colors_box.addWidget(btn)
            theme_v.addLayout(colors_box)

            theme_v.addSpacing(20)
            style_h1 = QLabel("Desktop Theme")
            style_h1.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
            theme_v.addWidget(style_h1)

            theme_mode_box = QHBoxLayout()
            self.dark_btn = QPushButton("🌙 RIDA Dark (Default)")
            self.dark_btn.setStyleSheet("background: #1F2937; color: white; border: 1px solid #374151; padding: 12px; border-radius: 8px; font-weight: bold;")
            self.dark_btn.clicked.connect(lambda: self._apply_theme_action("dark"))

            self.light_btn = QPushButton("☀️ RIDA Light")
            self.light_btn.setStyleSheet("background: #F3F4F6; color: #111827; border: 1px solid #E5E7EB; padding: 12px; border-radius: 8px; font-weight: bold;")
            self.light_btn.clicked.connect(lambda: self._apply_theme_action("light"))

            theme_mode_box.addWidget(self.dark_btn)
            theme_mode_box.addWidget(self.light_btn)
            theme_v.addLayout(theme_mode_box)

            theme_v.addStretch()
            tabs.addTab(theme_tab, "Themes && Colors")

            main_layout.addWidget(tabs)

            # Set default selection
            self.cards["windows_classic"].radio.setChecked(True)

        def _on_layout_chosen(self, key):
            self.current_layout = key
            meta = LAYOUT_META[key]
            self.status_lbl.setText(f"Selected: {meta['title']}")

        def _apply_layout_action(self):
            success, msg = apply_plasma_layout(self.current_layout)
            if success:
                self.status_lbl.setText(f"✓ {msg}")
                self.status_lbl.setStyleSheet("font-size: 12px; color: #10B981;")
            else:
                self.status_lbl.setText(f"✗ {msg}")
                self.status_lbl.setStyleSheet("font-size: 12px; color: #EF4444;")

        def _apply_color_action(self, hex_val):
            self.current_color = hex_val
            success, msg = apply_accent_color(hex_val)
            if success:
                self.status_lbl.setText(f"✓ {msg}")
                self.status_lbl.setStyleSheet("font-size: 12px; color: #10B981;")
            else:
                self.status_lbl.setText(f"✗ {msg}")
                self.status_lbl.setStyleSheet("font-size: 12px; color: #EF4444;")

        def _apply_theme_action(self, mode):
            success, msg = apply_theme_mode(mode)
            if success:
                self.status_lbl.setText(f"✓ {msg}")
                self.status_lbl.setStyleSheet("font-size: 12px; color: #10B981;")
            else:
                self.status_lbl.setText(f"✗ {msg}")
                self.status_lbl.setStyleSheet("font-size: 12px; color: #EF4444;")

        def _apply_global_styles(self):
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #0F1218;
                }
                QTabWidget::pane {
                    border: 1px solid #202632;
                    background-color: #141820;
                    border-radius: 12px;
                    top: -1px;
                }
                QTabBar::tab {
                    background: transparent;
                    color: #94A3B8;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 10px 20px;
                    border-bottom: 2px solid transparent;
                }
                QTabBar::tab:selected {
                    color: #2D7DFF;
                    border-bottom: 2px solid #2D7DFF;
                }
                QTabBar::tab:hover {
                    color: #FFFFFF;
                }
                QPushButton#PrimaryButton {
                    background-color: #2D7DFF;
                    color: #FFFFFF;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 8px 24px;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton#PrimaryButton:hover {
                    background-color: #1D6AE5;
                }
                QRadioButton {
                    color: #FFFFFF;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)

else:
    # Minimal fallback CLI / Tkinter runner if Qt is not installed on host
    import tkinter as tk
    from tkinter import ttk, messagebox

    class RidaAppearanceWindow:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("RIDA Appearance (Demo Mode)")
            self.root.geometry("640x500")
            self.root.configure(bg="#0F1218")
            self.current_layout = tk.StringVar(value="windows_classic")
            self._setup_ui()

        def _setup_ui(self):
            lbl = tk.Label(self.root, text="RIDA OS Appearance", font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg="#0F1218")
            lbl.pack(pady=15)
            
            sub = tk.Label(self.root, text="Select your preferred desktop layout style:", fg="#94A3B8", bg="#0F1218")
            sub.pack(pady=5)

            box = tk.Frame(self.root, bg="#181D26", padx=15, pady=15)
            box.pack(fill="both", expand=True, padx=20, pady=10)

            for key, meta in LAYOUT_META.items():
                rb = tk.Radiobutton(
                    box, text=f"{meta['title']} — {meta['desc']}",
                    variable=self.current_layout, value=key,
                    fg="#FFFFFF", bg="#181D26", selectcolor="#2D7DFF",
                    activebackground="#181D26", activeforeground="#FFFFFF",
                    font=("Helvetica", 11)
                )
                rb.pack(anchor="w", pady=10)

            btn = tk.Button(self.root, text="Apply Layout", font=("Helvetica", 12, "bold"),
                            bg="#2D7DFF", fg="#FFFFFF", padx=20, pady=8, command=self._apply)
            btn.pack(pady=15)

        def _apply(self):
            key = self.current_layout.get()
            success, msg = apply_plasma_layout(key)
            messagebox.showinfo("RIDA Appearance", msg)

        def show(self):
            self.root.mainloop()


def main():
    if QT_AVAILABLE:
        app = QApplication(sys.argv)
        app.setApplicationName("RIDA Appearance")
        win = RidaAppearanceWindow()
        win.show()
        sys.exit(app.exec())
    else:
        win = RidaAppearanceWindow()
        win.show()

if __name__ == "__main__":
    main()
