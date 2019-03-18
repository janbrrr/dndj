function playMusic(groupIndex, trackListIndex) {
    const xhr = new XMLHttpRequest();
    const url = "music/play/";
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            $(".playing").removeClass("playing");
            $("#music-" + groupIndex + "-" + trackListIndex).addClass("playing");
        } else if (this.readyState === XMLHttpRequest.DONE && this.status !== 200) {
            console.log("Error attempting to play music in group " + groupIndex + " at index " + trackListIndex);
        }
    };
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send("groupIndex=" + groupIndex + "&trackListIndex=" + trackListIndex);
}

function stopMusic() {
    const xhr = new XMLHttpRequest();
    const url = "music/stop/";
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            $(".playing").removeClass("playing");
        } else if (this.readyState === XMLHttpRequest.DONE && this.status !== 200) {
            console.log("Error attempting to stop music");
        }
    };
    xhr.open("POST", url);
    xhr.send();
}

function setMusicVolume() {
    const volume = $("#music-volume").val();
    const xhr = new XMLHttpRequest();
    const url = "music/volume/";
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status !== 200) {
            console.log("Error attempting to set music volume with value " + volume);
        }
    };
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send("volume=" + volume);
}