// Compact / Minimalist Layout for KDE Plasma (RIDA OS)
// Single compact top or bottom panel with simple menu and grouped tasklist

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    allPanels[i].remove();
}

var panel = new Panel();
panel.location = "top";
panel.height = 36;
panel.alignment = "left";

// Compact Application Menu
var menu = panel.addWidget("org.kde.plasma.kicker");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "rida-logo");

// Traditional Window List Task Manager
var taskManager = panel.addWidget("org.kde.plasma.tasks");

// Spacer
panel.addWidget("org.kde.plasma.panelspacer");

// System Tray
panel.addWidget("org.kde.plasma.systemtray");

// Digital Clock
panel.addWidget("org.kde.plasma.digitalclock");
