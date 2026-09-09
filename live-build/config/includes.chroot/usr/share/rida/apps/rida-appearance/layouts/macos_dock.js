// macOS / Cupertino Layout for KDE Plasma (RIDA OS)
// Top Menu/Status Bar + Bottom Floating Dock

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    allPanels[i].remove();
}

// 1. Top Status Bar
var topBar = new Panel();
topBar.location = "top";
topBar.height = 30;

// Application Launcher (Apple-style top left icon)
var launcher = topBar.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "rida-logo");

// Global Menu (File, Edit, View...)
topBar.addWidget("org.kde.plasma.appmenu");

// Spacer
topBar.addWidget("org.kde.plasma.panelspacer");

// Digital Clock in Top Center/Right
var clock = topBar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");

// System Tray
topBar.addWidget("org.kde.plasma.systemtray");

// 2. Bottom Floating Dock
var dock = new Panel();
dock.location = "bottom";
dock.height = 60;
dock.alignment = "center";
dock.floating = true;
dock.hiding = "windowscover"; // Auto-hide or dodge windows

var dockTasks = dock.addWidget("org.kde.plasma.icontasks");
dockTasks.currentConfigGroup = ["General"];
dockTasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:firefox-esr.desktop",
    "applications:org.kde.discover.desktop",
    "applications:vlc.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:systemsettings.desktop"
]);
dock.addWidget("org.kde.plasma.trash");
