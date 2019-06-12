function playSound(groupIndex, soundIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "playSound",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
    };
    conn.send(JSON.stringify(toSend));
}

function stopSound(groupIndex, soundIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "stopSound",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
    };
    conn.send(JSON.stringify(toSend));
}

function setSoundMasterVolume(volume) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "setSoundMasterVolume",
        "volume": volume,
    };
    conn.send(JSON.stringify(toSend));
}

function setSoundVolume(groupIndex, soundIndex, volume) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "setSoundVolume",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
        "volume": volume,
    };
    conn.send(JSON.stringify(toSend));
}