import QtQuick 2.5

Rectangle {
    id: root
    color: "#000000"

    property int stage: 0

    Item {
        anchors.centerIn: parent
        width: 320
        height: 320

        Image {
            id: logo
            anchors.centerIn: parent
            width: 280
            height: 280
            source: "rida-logo.png"
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
    }
}
