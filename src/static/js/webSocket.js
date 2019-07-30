let conn = null;
$(document).ready(function() {
    if (conn == null) {
        connect();
    } else {
        disconnect();
    }
});


function connect() {
    disconnect();
    const wsUri = (window.location.protocol==='https:'&&'wss://'||'ws://')+window.location.host;
    conn = new WebSocket(wsUri);
    conn.onopen = function() {
        console.log("Connected");
    };
    conn.onmessage = function(e) {
        const data = JSON.parse(e.data);
        switch (data.action) {
            case "nowPlaying": {
                _handleNowPlaying(data);
                break;
            }
            case "musicStopped": {
                _handleMusicStopped(data);
                break;
            }
            case "musicFinished": {
                _handleMusicFinished(data);
                break;
            }
            case "setMusicVolume": {
                _handleSetMusicVolume(data);
                break;
            }
            case "setSoundMasterVolume": {
                _handleSetSoundMasterVolume(data);
                break;
            }
            case "setSoundVolume": {
                _handleSetSoundVolume(data);
                break;
            }
            case "soundPlaying": {
                _handleSoundPlaying(data);
                break;
            }
            case "soundStopped": {
                _handleSoundStopped(data);
                break;
            }
            case "soundFinished": {
                _handleSoundFinished(data);
                break;
            }
            case "setSoundLoop": {
                _handleSetSoundLoop(data);
                break;
            }
            case "setSoundLoopDelay": {
                _handleSetSoundLoopDelay(data);
                break;
            }
            default:
                console.log("Received unknown action: " + data.action);
        }
    };
    conn.onclose = function() {
        console.log("Disconnected");
        conn = null;
    };
}

function disconnect() {
   if (conn != null) {
       conn.close();
       conn = null;
   }
}

function onNotConnected(){
    console.log("No connection established!");
    displayToast("Not Connected", "Please reload the page");
}

function displayToast(title, message) {
    const min = 1;
    const max = 1000;
    const randomNumber = Math.floor(Math.random() * (max - min)) + min;
    const randomId= "toast-" + randomNumber;
    const toast = `
        <div id="${randomId}" class="toast" role="status" aria-live="polite" aria-atomic="true" data-delay="5000" data-autohide="true">
          <div class="toast-header">
            <strong class="mr-auto">${title}</strong>
            <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="toast-body">
            ${message}
          </div>
        </div>
    `;
    $("#toast-container").append(toast);
    const toastSelector = $(`#${randomId}`);
    toastSelector.on('hidden.bs.toast', function () {
        $(this).remove();
    });
    toastSelector.toast("show");
}

function _handleNowPlaying(data) {
    $("#music .playing").removeClass("playing");
    $("#group-music-" + data.groupIndex).addClass("playing");
    $("#btn-music-" + data.groupIndex + "-" + data.trackListIndex).addClass("playing");
    $("#now-playing").text(`${data.groupName} > ${data.trackName}`);
    console.log("Now playing " + data.trackName + " (group " + data.groupIndex + " at index "
        + data.trackListIndex + ")");
    displayToast("Music", "Now playing <strong>" + data.trackName + "</strong>.");
}

function _handleMusicStopped(data) {
    $("#music .playing").removeClass("playing");
    $("#now-playing").text("-");
    console.log("Music stopped playing");
    displayToast("Music", "Stopped the music.");
}

function _handleMusicFinished(data) {
    $("#music .playing").removeClass("playing");
    $("#now-playing").text("-");
    console.log("Music finished playing");
    displayToast("Music", "Finished playing the music.");
}

function _handleSetMusicVolume(data) {
    $("#music-volume").slider('setValue', data.volume);
    console.log("Music volume set to " + data.volume);
    displayToast("Music", "Set volume to <strong>" + data.volume + "</strong>.");
}

function _handleSetSoundMasterVolume(data) {
    $("#sound-volume").slider('setValue', data.volume);
    console.log("Sound master volume set to " + data.volume);
    displayToast("Sound", "Set master volume to <strong>" + data.volume + "</strong>.");
}

function _handleSetSoundVolume(data) {
    $("#sound-volume-" + data.groupIndex + "-" + data.soundIndex).slider('setValue', data.volume);
    console.log("Sound volume for group=" + data.groupIndex + ", sound=" + data.soundIndex +
        " set to " + data.volume);
}

function _handleSoundPlaying(data) {
    $("#group-sound-" + data.groupIndex).addClass("playing");
    const soundDiv = $("#sound-" + data.groupIndex + "-" + data.soundIndex);
    const playButton = $("#btn-sound-play-" + data.groupIndex + "-" + data.soundIndex);
    const stopButton = $("#btn-sound-stop-" + data.groupIndex + "-" + data.soundIndex);
    soundDiv.addClass("playing");
    playButton.addClass("hidden");
    stopButton.removeClass("hidden").addClass("playing");
    console.log("Now playing sound " + data.soundName + " (group " + data.groupIndex + " at index "
        + data.soundIndex + ")");
}

function _handleSoundStopped(data){
    const soundDiv = $("#sound-" + data.groupIndex + "-" + data.soundIndex);
    const playButton = $("#btn-sound-play-" + data.groupIndex + "-" + data.soundIndex);
    const stopButton = $("#btn-sound-stop-" + data.groupIndex + "-" + data.soundIndex);
    soundDiv.removeClass("playing");
    stopButton.removeClass("playing").addClass("hidden");
    playButton.removeClass("hidden");
    const groupElement = $("#group-sound-" + data.groupIndex).parent();
    if (groupElement.find("div.playing").length === 0) {
        groupElement.children("a").removeClass("playing");
    }
    console.log("Stopped sound " + data.soundName + " (group " + data.groupIndex + " at index "
        + data.soundIndex + ")");
}

function _handleSoundFinished(data){
    const soundDiv = $("#sound-" + data.groupIndex + "-" + data.soundIndex);
    const playButton = $("#btn-sound-play-" + data.groupIndex + "-" + data.soundIndex);
    const stopButton = $("#btn-sound-stop-" + data.groupIndex + "-" + data.soundIndex);
    soundDiv.removeClass("playing");
    stopButton.removeClass("playing").addClass("hidden");
    playButton.removeClass("hidden");
    const groupElement = $("#group-sound-" + data.groupIndex).parent();
    if (groupElement.find("div.playing").length === 0) {
        groupElement.children("a").removeClass("playing");
    }
    console.log("Finished sound " + data.soundName + " (group " + data.groupIndex + " at index "
        + data.soundIndex + ")");
}

function _handleSetSoundLoop(data) {
    const soundLoopIcon = $("#btn-sound-loop-" + data.groupIndex + "-" + data.soundIndex);
    if (data.loop) {
        soundLoopIcon.addClass("looping");
    } else {
        soundLoopIcon.removeClass("looping");
    }
    console.log("Sound loop for group=" + data.groupIndex + ", sound=" + data.soundIndex +
        " set to " + data.loop);
}

function _handleSetSoundLoopDelay(data) {
    const soundLoopDelayInput = $("#sound-loop-delay-" + data.groupIndex + "-" + data.soundIndex);
    soundLoopDelayInput.val(data.loopDelay);
    console.log("Sound loop delay for group=" + data.groupIndex + ", sound=" + data.soundIndex +
        " set to " + data.loopDelay);
}
