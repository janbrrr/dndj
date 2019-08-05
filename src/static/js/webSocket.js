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
            case "setMusicMasterVolume": {
                _handleSetMusicMasterVolume(data);
                break;
            }
            case "setTrackListVolume": {
                _handleSetTrackListVolume(data);
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
    setMusicPlaying(data.groupIndex, data.groupName, data.trackListIndex, data.trackName);
    console.log("Now playing " + data.trackName + " (group " + data.groupIndex + " at index "
        + data.trackListIndex + ")");
    displayToast("Music", "Now playing <strong>" + data.trackName + "</strong>.");
}

function _handleMusicStopped(data) {
    setMusicNotPlaying();
    console.log("Music stopped playing");
    displayToast("Music", "Stopped the music.");
}

function _handleMusicFinished(data) {
    setMusicNotPlaying();
    console.log("Music finished playing");
    displayToast("Music", "Finished playing the music.");
}

function _handleSetMusicMasterVolume(data) {
    setMusicMasterVolume(data.volume);
    console.log("Music master volume set to " + data.volume);
}

function _handleSetTrackListVolume(data) {
    setTrackListVolumeSlider(data.groupIndex, data.trackListIndex, data.volume);
    console.log("music volume for group=" + data.groupIndex + ", trackList=" + data.trackListIndex +
        " set to " + data.volume);
}

function _handleSetSoundMasterVolume(data) {
    setSoundMasterVolume(data.volume);
    console.log("Sound master volume set to " + data.volume);
}

function _handleSetSoundVolume(data) {
    setSoundVolume(data.groupIndex, data.soundIndex, data.volume);
    console.log("Sound volume for group=" + data.groupIndex + ", sound=" + data.soundIndex +
        " set to " + data.volume);
}

function _handleSoundPlaying(data) {
    setSoundPlaying(data.groupIndex, data.soundIndex);
    console.log("Now playing sound " + data.soundName + " (group " + data.groupIndex + " at index "
        + data.soundIndex + ")");
}

function _handleSoundStopped(data){
    setSoundNotPlaying(data.groupIndex, data.soundIndex);
    console.log("Stopped sound " + data.soundName + " (group " + data.groupIndex + " at index "
        + data.soundIndex + ")");
}

function _handleSoundFinished(data){
    setSoundNotPlaying(data.groupIndex, data.soundIndex);
    console.log("Finished sound " + data.soundName + " (group " + data.groupIndex + " at index "
        + data.soundIndex + ")");
}

function _handleSetSoundLoop(data) {
    setSoundLoop(data.groupIndex, data.soundIndex, data.loop);
    console.log("Sound loop for group=" + data.groupIndex + ", sound=" + data.soundIndex +
        " set to " + data.loop);
}

function _handleSetSoundLoopDelay(data) {
    setSoundLoopDelay(data.groupIndex, data.soundIndex, data.loopDelay);
    console.log("Sound loop delay for group=" + data.groupIndex + ", sound=" + data.soundIndex +
        " set to " + data.loopDelay);
}
