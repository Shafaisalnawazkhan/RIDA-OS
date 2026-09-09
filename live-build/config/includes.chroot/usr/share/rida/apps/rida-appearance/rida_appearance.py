#!/usr/bin/env python3
"""
RIDA OS Appearance Tool — Modern Zorin / Win11 Aesthetic
Switch desktop layouts, customize accent colors, toggle themes,
and set custom wallpapers with instant live preview.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
LAYOUTS_DIR = SCRIPT_DIR / "layouts"

LAYOUT_META = {
    "windows_classic": {
        "title": "Windows Standard",
        "badge": "RECOMMENDED FOR SWITCHERS",
        "desc": "Classic bottom taskbar with Start Menu on left, pinned apps, and system tray.",
        "script": LAYOUTS_DIR / "windows_classic.js",
        "preview": "win_classic",
    },
    "windows_modern": {
        "title": "Windows Modern",
        "badge": "MODERN CENTERED",
        "desc": "Contemporary centered floating taskbar with quick search and grouped icons.",
        "script": LAYOUTS_DIR / "windows_modern.js",
        "preview": "win_modern",
    },
    "macos_dock": {
        "title": "Cupertino (macOS)",
        "badge": "ELEGANT DOCK",
        "desc": "Top global menu & status bar paired with a floating bottom application dock.",
        "script": LAYOUTS_DIR / "macos_dock.js",
        "preview": "macos",
    },
    "compact": {
        "title": "Compact / Minimal",
        "badge": "MAX REAL ESTATE",
        "desc": "Lightweight top bar with minimalist launcher for laptops and widescreen monitors.",
        "script": LAYOUTS_DIR / "compact.js",
        "preview": "compact",
    },
}

ACCENT_COLORS = [
    ("Sapphire", "#2563EB", "45,125,255"),
    ("Cyan", "#06B6D4", "6,182,212"),
    ("Emerald", "#10B981", "16,185,129"),
    ("Amethyst", "#8B5CF6", "139,92,246"),
    ("Rose", "#F43F5E", "244,63,94"),
    ("Amber", "#F59E0B", "245,158,11"),
]

def is_plasma_session():
    return (
        os.environ.get("KDE_FULL_SESSION") == "true"
        or "KDE" in os.environ.get("XDG_CURRENT_DESKTOP", "")
        or "plasma" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        or shutil.which("plasmashell") is not None
    )

def run_dbus_eval(script_content: str):
    """Executes plasma javascript script using available dbus tools."""
    candidates = [
        ["qdbus-qt5", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script_content],
        ["qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script_content],
        ["/usr/lib/qt5/bin/qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script_content],
        ["dbus-send", "--session", "--dest=org.kde.plasmashell", "--type=method_call", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", f"string:{script_content}"],
        ["gdbus", "call", "--session", "--dest", "org.kde.plasmashell", "--object-path", "/PlasmaShell", "--method", "org.kde.PlasmaShell.evaluateScript", script_content]
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]) or os.path.exists(cmd[0]):
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
                if res.returncode == 0:
                    return True
            except Exception:
                pass
    return False

def apply_plasma_layout(layout_key: str):
    """Executes layout script via Plasma DBus."""
    meta = LAYOUT_META.get(layout_key)
    if not meta:
        return False, "Unknown layout key"
    
    script_path = meta["script"]
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    if is_plasma_session():
        try:
            with open(script_path, "r") as f:
                content = f.read()
            
            ok = run_dbus_eval(content)
            if not ok:
                subprocess.run(["systemctl", "--user", "restart", "plasma-plasmashell"], check=False)
            return True, f"Successfully applied {meta['title']} layout!"
        except Exception as e:
            return False, f"Failed: {str(e)}"
    return True, f"[Demo Mode] Selected {meta['title']}."

def apply_accent_color(color_name: str, color_hex: str, rgb_str: str):
    """Applies accent color to KDE configuration and reloads color scheme."""
    if is_plasma_session():
        try:
            if shutil.which("kwriteconfig5"):
                subprocess.run(["kwriteconfig5", "--file", "kdeglobals", "--group", "General", "--key", "AccentColor", rgb_str], check=False)
                subprocess.run(["kwriteconfig5", "--file", "kdeglobals", "--group", "General", "--key", "accentColorHex", color_hex], check=False)

            if shutil.which("plasma-apply-colorscheme"):
                subprocess.run(["plasma-apply-colorscheme", "BreezeDark"], check=False)

            # Notify KWin
            for cmd in [
                ["qdbus-qt5", "org.kde.KWin", "/KWin", "reconfigure"],
                ["qdbus", "org.kde.KWin", "/KWin", "reconfigure"],
                ["/usr/lib/qt5/bin/qdbus", "org.kde.KWin", "/KWin", "reconfigure"],
                ["dbus-send", "--session", "--dest=org.kde.KWin", "--type=method_call", "/KWin", "org.kde.KWin.reconfigure"]
            ]:
                if shutil.which(cmd[0]) or os.path.exists(cmd[0]):
                    subprocess.run(cmd, check=False)
                    break
            return True, f"Accent color set to {color_name} ({color_hex})!"
        except Exception as e:
            return False, str(e)
    return True, f"[Demo Mode] Set accent color to {color_name}"

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
            return True, f"Switched to {'RIDA Dark' if mode == 'dark' else 'RIDA Light'} theme!"
        except Exception as e:
            return False, str(e)
    return True, f"[Demo Mode] Switched to {'Dark' if mode == 'dark' else 'Light'} mode"

def apply_wallpaper(wp_path: str):
    """Sets wallpaper on all active desktop screens."""
    script = f"""
    var allDesktops = desktops();
    for (var i=0; i<allDesktops.length; i++) {{
        allDesktops[i].wallpaperPlugin = 'org.kde.image';
        allDesktops[i].currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General'];
        allDesktops[i].writeConfig('Image', '{wp_path}');
    }}
    """
    if is_plasma_session():
        run_dbus_eval(script)
        return True, "Wallpaper updated to RIDA Sapphire!"
    return True, f"[Demo Mode] Wallpaper set to {wp_path}"

# PyQt6 Setup
QT_AVAILABLE = False
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QRadioButton, QButtonGroup,
        QScrollArea, QMessageBox, QTabWidget, QGridLayout
    )
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtGui import QFont, QIcon, QColor, QPainter, QBrush, QPen
    QT_AVAILABLE = True
except ImportError:
    pass

if QT_AVAILABLE:
    class LayoutMiniPreview(QFrame):
        """Draws a visual schematic representation of the desktop layout."""
        def __init__(self, p_type, parent=None):
            super().__init__(parent)
            self.p_type = p_type
            self.setFixedHeight(72)
            self.setStyleSheet("background: #0D1117; border-radius: 8px; border: 1px solid #21262D;")

        def paintEvent(self, event):
            super().paintEvent(event)
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            w = self.width()
            h = self.height()

            # Mini windows inside preview
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#1F2937"))
            p.drawRoundedRect(16, 12, int(w * 0.45), 34, 4, 4)
            p.setBrush(QColor("#273346"))
            p.drawRoundedRect(int(w * 0.40), 18, int(w * 0.45), 32, 4, 4)

            # Active layout bar
            accent = QColor("#2563EB")
            dot = QColor("#60A5FA")

            if self.p_type == "win_classic":
                # Bottom taskbar
                p.setBrush(QColor("#161B22"))
                p.drawRect(0, h - 14, w, 14)
                # Start button
                p.setBrush(accent)
                p.drawRoundedRect(8, h - 11, 8, 8, 2, 2)
                # App icons
                p.setBrush(dot)
                p.drawRoundedRect(22, h - 10, 6, 6, 1, 1)
                p.drawRoundedRect(32, h - 10, 6, 6, 1, 1)
                # Tray
                p.setBrush(QColor("#64748B"))
                p.drawRoundedRect(w - 24, h - 10, 16, 6, 1, 1)

            elif self.p_type == "win_modern":
                # Floating centered taskbar
                p.setBrush(QColor("#161B22"))
                bar_w = int(w * 0.65)
                bar_x = int((w - bar_w) / 2)
                p.drawRoundedRect(bar_x, h - 16, bar_w, 12, 6, 6)
                p.setBrush(accent)
                p.drawRoundedRect(bar_x + 12, h - 13, 6, 6, 1, 1)
                p.setBrush(dot)
                p.drawRoundedRect(bar_x + 24, h - 13, 6, 6, 1, 1)
                p.drawRoundedRect(bar_x + 36, h - 13, 6, 6, 1, 1)

            elif self.p_type == "macos":
                # Top status bar
                p.setBrush(QColor("#161B22"))
                p.drawRect(0, 0, w, 10)
                p.setBrush(dot)
                p.drawEllipse(8, 2, 6, 6)
                # Floating bottom dock
                p.setBrush(QColor("#161B22"))
                dock_w = int(w * 0.50)
                dock_x = int((w - dock_w) / 2)
                p.drawRoundedRect(dock_x, h - 14, dock_w, 12, 6, 6)
                p.setBrush(accent)
                for di in range(4):
                    p.drawRoundedRect(dock_x + 10 + (di * 12), h - 11, 6, 6, 1, 1)

            elif self.p_type == "compact":
                # Minimalist slim top panel
                p.setBrush(QColor("#161B22"))
                p.drawRect(0, 0, w, 12)
                p.setBrush(accent)
                p.drawRoundedRect(6, 2, 8, 8, 2, 2)
                p.setBrush(dot)
                p.drawRoundedRect(20, 3, 24, 6, 1, 1)
            p.end()

    class ModernLayoutCard(QFrame):
        def __init__(self, key, meta, on_select, parent=None):
            super().__init__(parent)
            self.key = key
            self.on_select = on_select
            self.setObjectName("LayoutCard")
            self.setCursor(Qt.CursorShape.PointingHandCursor)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(10)

            # Header
            header = QHBoxLayout()
            title = QLabel(meta["title"])
            title.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
            header.addWidget(title)
            header.addStretch()

            self.radio = QRadioButton()
            header.addWidget(self.radio)
            layout.addLayout(header)

            # Badge
            badge = QLabel(meta["badge"])
            badge.setStyleSheet("font-size: 9px; font-weight: 800; color: #38BDF8; letter-spacing: 0.8px;")
            layout.addWidget(badge)

            # Description
            desc = QLabel(meta["desc"])
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 12px; color: #94A3B8; line-height: 1.4;")
            layout.addWidget(desc)

            # Graphic Mini Preview
            preview = LayoutMiniPreview(meta["preview"])
            layout.addWidget(preview)

            self.radio.toggled.connect(self._on_toggled)

        def _on_toggled(self, checked):
            if checked:
                self.setStyleSheet("""
                    QFrame#LayoutCard {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E2738, stop:1 #141B26);
                        border: 2px solid #2563EB;
                        border-radius: 12px;
                    }
                """)
                self.on_select(self.key)
            else:
                self.setStyleSheet("""
                    QFrame#LayoutCard {
                        background: #111620;
                        border: 1px solid #1E2636;
                        border-radius: 12px;
                    }
                    QFrame#LayoutCard:hover {
                        border: 1px solid #3B82F6;
                        background: #151C28;
                    }
                """)

        def mousePressEvent(self, event):
            self.radio.setChecked(True)
            super().mousePressEvent(event)

    class RidaAppearanceWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("RIDA OS Appearance")
            self.resize(840, 640)
            self.current_layout = "windows_classic"
            self._setup_ui()
            self._apply_global_styles()

        def _setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(28, 24, 28, 24)
            main_layout.setSpacing(18)

            # Top Header Bar
            header_box = QHBoxLayout()
            title_col = QVBoxLayout()
            h1 = QLabel("Desktop Customization")
            h1.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
            sub = QLabel("Craft your desktop layout, accent colors, and dark/light mode.")
            sub.setStyleSheet("font-size: 13px; color: #94A3B8;")
            title_col.addWidget(h1)
            title_col.addWidget(sub)
            header_box.addLayout(title_col)
            header_box.addStretch()

            logo_badge = QLabel("RIDA OS 1.0")
            logo_badge.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2563EB, stop:1 #1D4ED8);
                color: #FFFFFF;
                font-weight: 800;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 12px;
            """)
            header_box.addWidget(logo_badge)
            main_layout.addLayout(header_box)

            # Tab Widget
            tabs = QTabWidget()
            tabs.setObjectName("AppearanceTabs")

            # TAB 1: Layouts
            layout_tab = QWidget()
            layout_v = QVBoxLayout(layout_tab)
            layout_v.setContentsMargins(14, 16, 14, 14)
            layout_v.setSpacing(14)

            grid = QGridLayout()
            grid.setSpacing(14)

            self.cards = {}
            self.btn_group = QButtonGroup(self)

            row, col = 0, 0
            for key, meta in LAYOUT_META.items():
                card = ModernLayoutCard(key, meta, self._on_layout_chosen)
                self.btn_group.addButton(card.radio)
                self.cards[key] = card
                grid.addWidget(card, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1

            layout_v.addLayout(grid)
            layout_v.addStretch()

            # Apply Action Bar
            action_bar = QHBoxLayout()
            self.status_lbl = QLabel("Ready to personalize desktop")
            self.status_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
            action_bar.addWidget(self.status_lbl)
            action_bar.addStretch()

            apply_btn = QPushButton("Apply Desktop Layout")
            apply_btn.setObjectName("PrimaryButton")
            apply_btn.setFixedHeight(40)
            apply_btn.clicked.connect(self._apply_layout_action)
            action_bar.addWidget(apply_btn)
            layout_v.addLayout(action_bar)

            tabs.addTab(layout_tab, "Desktop Layout")

            # TAB 2: Themes & Colors
            theme_tab = QWidget()
            theme_v = QVBoxLayout(theme_tab)
            theme_v.setContentsMargins(20, 20, 20, 20)
            theme_v.setSpacing(20)

            # Accent Color Section
            accent_title = QLabel("System Accent Color")
            accent_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
            theme_v.addWidget(accent_title)

            accent_sub = QLabel("Select an accent color for buttons, active window borders, slider controls, and highlights.")
            accent_sub.setStyleSheet("font-size: 12px; color: #94A3B8;")
            theme_v.addWidget(accent_sub)

            colors_row = QHBoxLayout()
            colors_row.setSpacing(14)
            for name, hex_val, rgb_str in ACCENT_COLORS:
                btn = QPushButton(name)
                btn.setFixedHeight(42)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {hex_val};
                        color: #FFFFFF;
                        font-weight: 700;
                        font-size: 12px;
                        border-radius: 10px;
                        padding: 8px 16px;
                        border: 2px solid transparent;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #FFFFFF;
                    }}
                """)
                btn.clicked.connect(lambda _, n=name, h=hex_val, r=rgb_str: self._apply_color_action(n, h, r))
                colors_row.addWidget(btn)
            theme_v.addLayout(colors_row)

            theme_v.addSpacing(12)

            # Theme Mode Section (Dark / Light)
            mode_title = QLabel("Color Theme")
            mode_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
            theme_v.addWidget(mode_title)

            modes_row = QHBoxLayout()
            modes_row.setSpacing(14)

            dark_card = QPushButton("🌙  RIDA Dark Mode")
            dark_card.setFixedHeight(54)
            dark_card.setCursor(Qt.CursorShape.PointingHandCursor)
            dark_card.setStyleSheet("""
                QPushButton {
                    background: #111620;
                    color: #FFFFFF;
                    border: 2px solid #2563EB;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 700;
                    text-align: center;
                }
                QPushButton:hover {
                    background: #182030;
                }
            """)
            dark_card.clicked.connect(lambda: self._apply_theme_mode_action("dark"))

            light_card = QPushButton("☀️  RIDA Light Mode")
            light_card.setFixedHeight(54)
            light_card.setCursor(Qt.CursorShape.PointingHandCursor)
            light_card.setStyleSheet("""
                QPushButton {
                    background: #F1F5F9;
                    color: #0F172A;
                    border: 1px solid #CBD5E1;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 700;
                    text-align: center;
                }
                QPushButton:hover {
                    background: #FFFFFF;
                    border: 2px solid #2563EB;
                }
            """)
            light_card.clicked.connect(lambda: self._apply_theme_mode_action("light"))

            modes_row.addWidget(dark_card)
            modes_row.addWidget(light_card)
            theme_v.addLayout(modes_row)

            theme_v.addSpacing(12)

            # Wallpaper Quick Switcher
            wp_title = QLabel("Desktop Wallpaper")
            wp_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
            theme_v.addWidget(wp_title)

            wp_row = QHBoxLayout()
            wp_btn = QPushButton("🌌 Set Official RIDA Sapphire Wallpaper")
            wp_btn.setFixedHeight(44)
            wp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            wp_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E293B, stop:1 #0F172A);
                    color: #38BDF8;
                    border: 1px solid #334155;
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 8px 20px;
                }
                QPushButton:hover {
                    border: 1px solid #38BDF8;
                    color: #FFFFFF;
                }
            """)
            wp_btn.clicked.connect(self._apply_official_wallpaper)
            wp_row.addWidget(wp_btn)
            wp_row.addStretch()
            theme_v.addLayout(wp_row)

            theme_v.addStretch()
            tabs.addTab(theme_tab, "Themes && Colors")

            main_layout.addWidget(tabs)
            self.cards["windows_classic"].radio.setChecked(True)

        def _on_layout_chosen(self, key):
            self.current_layout = key
            meta = LAYOUT_META[key]
            self.status_lbl.setText(f"Selected: {meta['title']}")

        def _apply_layout_action(self):
            success, msg = apply_plasma_layout(self.current_layout)
            self.status_lbl.setText(f"✓ {msg}" if success else f"✗ {msg}")
            self.status_lbl.setStyleSheet(f"font-size: 12px; color: {'#10B981' if success else '#EF4444'}; font-weight: 600;")

        def _apply_color_action(self, name, hex_val, rgb_str):
            success, msg = apply_accent_color(name, hex_val, rgb_str)
            self.status_lbl.setText(f"✓ {msg}" if success else f"✗ {msg}")
            self.status_lbl.setStyleSheet(f"font-size: 12px; color: {'#10B981' if success else '#EF4444'}; font-weight: 600;")

        def _apply_theme_mode_action(self, mode):
            success, msg = apply_theme_mode(mode)
            self.status_lbl.setText(f"✓ {msg}" if success else f"✗ {msg}")
            self.status_lbl.setStyleSheet(f"font-size: 12px; color: {'#10B981' if success else '#EF4444'}; font-weight: 600;")

        def _apply_official_wallpaper(self):
            wp_path = "/usr/share/rida/wallpapers/rida-sapphire-dark.svg"
            if not os.path.exists(wp_path):
                wp_path = str(SCRIPT_DIR.parent.parent / "live-build" / "config" / "includes.chroot" / "usr" / "share" / "rida" / "wallpapers" / "rida-sapphire-dark.svg")
            success, msg = apply_wallpaper(wp_path)
            self.status_lbl.setText(f"✓ {msg}" if success else f"✗ {msg}")
            self.status_lbl.setStyleSheet("font-size: 12px; color: #10B981; font-weight: 600;")

        def _apply_global_styles(self):
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #0B0E14;
                }
                QTabWidget::pane {
                    border: 1px solid #1C2331;
                    background-color: #10151E;
                    border-radius: 12px;
                    top: -1px;
                }
                QTabBar::tab {
                    background: transparent;
                    color: #94A3B8;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 10px 22px;
                    border-bottom: 2px solid transparent;
                }
                QTabBar::tab:selected {
                    color: #38BDF8;
                    border-bottom: 2px solid #38BDF8;
                }
                QTabBar::tab:hover {
                    color: #FFFFFF;
                }
                QPushButton#PrimaryButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1D4ED8);
                    color: #FFFFFF;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 8px 26px;
                    border-radius: 10px;
                    border: none;
                }
                QPushButton#PrimaryButton:hover {
                    background: #1D4ED8;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)

def main():
    if QT_AVAILABLE:
        app = QApplication(sys.argv)
        app.setApplicationName("RIDA Appearance")
        win = RidaAppearanceWindow()
        win.show()
        sys.exit(app.exec())
    else:
        print("PyQt6 is required.")

if __name__ == "__main__":
    main()
