function sendCmdPlayMusic(groupIndex, trackListIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "playMusic",
        "groupIndex": groupIndex,
        "trackListIndex": trackListIndex,
    };
    conn.send(JSON.stringify(toSend));
}


function sendCmdStopMusic() {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "stopMusic",
    };
    conn.send(JSON.stringify(toSend));
}

function sendCmdSetMusicMasterVolume(volume) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "setMusicMasterVolume",
        "volume": volume,
    };
    conn.send(JSON.stringify(toSend));
}

function sendCmdSetTrackListVolume(groupIndex, trackListIndex, volume) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "setTrackListVolume",
        "groupIndex": groupIndex,
        "trackListIndex": trackListIndex,
        "volume": volume,
    };
    conn.send(JSON.stringify(toSend));
}
