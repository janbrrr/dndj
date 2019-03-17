function playSound(groupIndex, soundIndex) {
    const xhr = new XMLHttpRequest();
    const url = "sound/play/";
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status !== 200) {
            console.log("Error attempting to play sound at index " + index);
        }
    };
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send("groupIndex=" + groupIndex + "&soundIndex=" + soundIndex);
}

function setSoundVolume() {
    const volume = $("#sound-volume").val();
    const xhr = new XMLHttpRequest();
    const url = "sound/volume/";
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status !== 200) {
            console.log("Error attempting to set sound volume with value " + volume);
        }
    };
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send("volume=" + volume);
}