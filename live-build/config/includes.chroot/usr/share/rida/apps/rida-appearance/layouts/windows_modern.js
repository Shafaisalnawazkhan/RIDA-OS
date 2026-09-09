// Windows Modern (Centered) Layout for KDE Plasma (RIDA OS)
// Centered icons with left-aligned or centered launcher, sleek floating appearance

var allPanels = panels();
for (var i = allPanels.length - 1; i >= 0; i--) {
    allPanels[i].remove();
}

var panel = new Panel();
panel.location = "bottom";
panel.height = 48;
panel.alignment = "center";
panel.floating = true; // Plasma 5.25+ floating panel support

// Left Spacer
panel.addWidget("org.kde.plasma.panelspacer");

// 1. Start Menu (Application Launcher)
var kickOff = panel.addWidget("org.kde.plasma.kickoff");
kickOff.currentConfigGroup = ["General"];
kickOff.writeConfig("icon", "rida-logo");

// 2. Search Button
panel.addWidget("org.kde.plasma.quicklaunch");

// 3. Centered Icons-Only Task Manager
var taskManager = panel.addWidget("org.kde.plasma.icontasks");
taskManager.currentConfigGroup = ["General"];
taskManager.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:firefox-esr.desktop",
    "applications:org.kde.discover.desktop",
    "applications:org.kde.konsole.desktop"
]);

// Right Spacer
panel.addWidget("org.kde.plasma.panelspacer");

// 4. System Tray
panel.addWidget("org.kde.plasma.systemtray");

// 5. Digital Clock
var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");

// 6. Show Desktop
panel.addWidget("org.kde.plasma.showdesktop");
