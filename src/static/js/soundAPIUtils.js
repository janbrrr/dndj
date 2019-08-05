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

function sendCmdSetSoundLoop(groupIndex, soundIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "setSoundLoop",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
        "loop": !isSoundLooping(groupIndex, soundIndex),
    };
    conn.send(JSON.stringify(toSend));
}

function sendCmdSetSoundLoopDelay(groupIndex, soundIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const toSend = {
        "action": "setSoundLoopDelay",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
        "loopDelay": selectSoundLoopDelayInput(groupIndex, soundIndex).val(),
    };
    conn.send(JSON.stringify(toSend));
}
