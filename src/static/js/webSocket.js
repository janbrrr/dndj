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
                $("#music .playing").removeClass("playing");
                $("#group-music-" + data.groupIndex).addClass("playing");
                $("#btn-music-" + data.groupIndex + "-" + data.trackListIndex).addClass("playing");
                $("#now-playing").text(`${data.groupName} > ${data.trackName}`);
                console.log("Now playing " + data.trackName + " (group " + data.groupIndex + " at index "
                    + data.trackListIndex + ")");
                displayToast("Music", "Now playing <strong>" + data.trackName + "</strong>.");
                break;
            }
            case "musicStopped": {
                $("#music .playing").removeClass("playing");
                $("#now-playing").text("-");
                console.log("Music stopped playing");
                displayToast("Music", "Stopped the music.");
                break;
            }
            case "musicFinished": {
                $("#music .playing").removeClass("playing");
                $("#now-playing").text("-");
                console.log("Music finished playing");
                displayToast("Music", "Finished playing the music.");
                break;
            }
            case "setMusicVolume": {
                $("#music-volume").slider('setValue', data.volume);
                console.log("Music volume set to " + data.volume);
                displayToast("Music", "Set volume to <strong>" + data.volume + "</strong>.");
                break;
            }
            case "setSoundMasterVolume": {
                $("#sound-volume").slider('setValue', data.volume);
                console.log("Sound master volume set to " + data.volume);
                displayToast("Sound", "Set master volume to <strong>" + data.volume + "</strong>.");
                break;
            }
            case "setSoundVolume": {
                $("#sound-volume-" + data.groupIndex + "-" + data.soundIndex).slider('setValue', data.volume);
                console.log("Sound volume for group=" + data.groupIndex + ", sound=" + data.soundIndex +
                    "set to " + data.volume);
                break;
            }
            case "soundPlaying": {
                $("#group-sound-" + data.groupIndex).addClass("playing");
                $("#btn-sound-" + data.groupIndex + "-" + data.soundIndex).addClass("playing");
                console.log("Now playing sound " + data.soundName + " (group " + data.groupIndex + " at index "
                    + data.soundIndex + ")");
                break;
            }
            case "soundStopped": {
                $("#btn-sound-" + data.groupIndex + "-" + data.soundIndex).removeClass("playing");
                const groupElement = $("#group-sound-" + data.groupIndex);
                if (groupElement.find(".playing").length === 0) {
                    groupElement.removeClass("playing");
                }
                console.log("Stopped sound " + data.soundName + " (group " + data.groupIndex + " at index "
                    + data.soundIndex + ")");
                break;
            }
            case "soundFinished": {
                $("#btn-sound-" + data.groupIndex + "-" + data.soundIndex).removeClass("playing");
                const groupElement = $("#group-sound-" + data.groupIndex);
                if (groupElement.find(".playing").length === 0) {
                    groupElement.removeClass("playing");
                }
                console.log("Finished sound " + data.soundName + " (group " + data.groupIndex + " at index "
                    + data.soundIndex + ")");
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
