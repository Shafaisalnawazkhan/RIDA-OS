import QtQuick 2.0
import QtQuick.Layouts 1.2
import QtQuick.Controls 2.5

Item {
    id: presentation
    anchors.fill: parent

    Timer {
        interval: 8000
        running: true
        repeat: true
        onTriggered: {
            swipeView.currentIndex = (swipeView.currentIndex + 1) % swipeView.count
        }
    }

    SwipeView {
        id: swipeView
        anchors.fill: parent
        currentIndex: 0

        // Slide 1: Welcome
        Item {
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 16
                Text {
                    text: "Welcome to RIDA OS"
                    font.pixelSize: 26
                    font.bold: true
                    color: "#FFFFFF"
                    Layout.alignment: Qt.AlignHCenter
                }
                Text {
                    text: "Debian Stability meets Modern Elegance"
                    font.pixelSize: 15
                    color: "#2D7DFF"
                    Layout.alignment: Qt.AlignHCenter
                }
                Text {
                    text: "Enjoy a familiar, responsive desktop engineered for productivity and reliability."
                    font.pixelSize: 13
                    color: "#94A3B8"
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }

        // Slide 2: Zorin-Style Appearance
        Item {
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 16
                Text {
                    text: "Tailored to Your Workflow"
                    font.pixelSize: 24
                    font.bold: true
                    color: "#FFFFFF"
                    Layout.alignment: Qt.AlignHCenter
                }
                Text {
                    text: "Switch effortlessly between Windows Classic, Modern Centered, or macOS layouts."
                    font.pixelSize: 14
                    color: "#94A3B8"
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }

        // Slide 3: Software & Flatpak
        Item {
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 16
                Text {
                    text: "Thousands of Apps with Flatpak & Discover"
                    font.pixelSize: 24
                    font.bold: true
                    color: "#FFFFFF"
                    Layout.alignment: Qt.AlignHCenter
                }
                Text {
                    text: "Discover brings together Debian's extensive repositories and Flathub's vast library."
                    font.pixelSize: 14
                    color: "#94A3B8"
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
    }

    PageIndicator {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 20
        count: swipeView.count
        currentIndex: swipeView.currentIndex
    }
}
