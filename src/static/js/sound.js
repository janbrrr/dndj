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

function setSoundLoop(groupIndex, soundIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const currentValue = $("#btn-sound-loop-" + groupIndex + "-" + soundIndex).hasClass("looping");
    const toSend = {
        "action": "setSoundLoop",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
        "loop": !currentValue,
    };
    conn.send(JSON.stringify(toSend));
}

function setSoundLoopDelay(groupIndex, soundIndex) {
    if (conn === null) {
        onNotConnected();
        return;
    }
    const inputElement = $("#sound-loop-delay-" + groupIndex + "-" + soundIndex);
    const toSend = {
        "action": "setSoundLoopDelay",
        "groupIndex": groupIndex,
        "soundIndex": soundIndex,
        "loopDelay": inputElement.val(),
    };
    conn.send(JSON.stringify(toSend));
}
