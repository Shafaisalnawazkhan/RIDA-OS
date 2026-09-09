// Windows Classic Layout for KDE Plasma (RIDA OS)
// Bottom panel with Application Menu (left), Icons-Only Task Manager (left/center), System Tray (right), Clock (far right)

var allPanels = panels();
for (var i = allPanels.length - 1; i >= 0; i--) {
    allPanels[i].remove();
}

var panel = new Panel();
panel.location = "bottom";
panel.height = 44;
panel.alignment = "left";

// 1. Start Menu (Application Launcher)
var kickOff = panel.addWidget("org.kde.plasma.kickoff");
kickOff.currentConfigGroup = ["General"];
kickOff.writeConfig("icon", "rida-logo");
kickOff.writeConfig("favoritesPortedToKAstats", "true");

// 2. Search / KRunner Button
panel.addWidget("org.kde.plasma.quicklaunch");

// 3. Icons-only Task Manager (Pinned apps + running windows)
var taskManager = panel.addWidget("org.kde.plasma.icontasks");
taskManager.currentConfigGroup = ["General"];
taskManager.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:firefox-esr.desktop",
    "applications:org.kde.discover.desktop",
    "applications:org.kde.konsole.desktop"
]);

// 4. Spacer to push system tray to the right
panel.addWidget("org.kde.plasma.panelspacer");

// 5. System Tray (Network, Volume, Battery, Notifications)
panel.addWidget("org.kde.plasma.systemtray");

// 6. Digital Clock
var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");

// 7. Show Desktop Widget (Far right peek)
panel.addWidget("org.kde.plasma.showdesktop");
