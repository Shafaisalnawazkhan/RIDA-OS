import QtQuick 2.5

Rectangle {
    id: root
    color: "#080C14"

    property int stage: 0

    Item {
        anchors.centerIn: parent
        width: 320
        height: 220

        Image {
            id: logo
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            width: 100
            height: 100
            source: "/usr/share/rida/icons/rida-logo.svg"
            fillMode: Image.PreserveAspectFit
            smooth: true
        }

        Text {
            id: title
            anchors.top: logo.bottom
            anchors.topMargin: 16
            anchors.horizontalCenter: parent.horizontalCenter
            text: "RIDA OS"
            color: "#FFFFFF"
            font.pixelSize: 24
            font.bold: true
        }

        Text {
            id: subtitle
            anchors.top: title.bottom
            anchors.topMargin: 6
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Starting desktop..."
            color: "#38BDF8"
            font.pixelSize: 12
            font.bold: true
        }
    }
}
