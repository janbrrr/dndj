function sendCmdPlaySound(groupIndex, soundIndex) {
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

function sendCmdStopSound(groupIndex, soundIndex) {
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

function sendCmdSetSoundMasterVolume(volume) {
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

function sendCmdSetSoundVolume(groupIndex, soundIndex, volume) {
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

function sendCmdSetSoundRepeatCount(groupIndex, soundIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "setSoundRepeatCount",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
        "repeatCount": selectSoundRepeatCountInput(groupIndex, soundIndex).val(),
    };
    conn.send(JSON.stringify(toSend));
}

function sendCmdSetSoundRepeatDelay(groupIndex, soundIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "setSoundRepeatDelay",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
        "repeatDelay": selectSoundRepeatDelayInput(groupIndex, soundIndex).val(),
    };
    conn.send(JSON.stringify(toSend));
}
