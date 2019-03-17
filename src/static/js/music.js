function playMusic(index) {
    const xhr = new XMLHttpRequest();
    const url = "music/play/";
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            $(".playing").removeClass("playing");
            $("#music-" + index).addClass("playing");
        } else if (this.readyState === XMLHttpRequest.DONE && this.status !== 200) {
            console.log("Error attempting to play music at index " + index);
        }
    };
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send("index=" + index);
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