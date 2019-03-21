function playMusic(groupIndex, trackListIndex) {
    if (conn === null) {
        console.log("No connection established!");
        return;
    }
    const toSend = {
        "action": "playMusic",
        "groupIndex": groupIndex,
        "trackListIndex": trackListIndex,
    };
    conn.send(JSON.stringify(toSend));
}


function stopMusic() {
    if (conn === null) {
        console.log("No connection established!");
        return;
    }
    const toSend = {
        "action": "stopMusic",
    };
    conn.send(JSON.stringify(toSend));
}

function setMusicVolume(volume) {
    if (conn === null) {
        console.log("No connection established!");
        return;
    }
    const toSend = {
        "action": "setMusicVolume",
        "volume": volume,
    };
    conn.send(JSON.stringify(toSend));
}