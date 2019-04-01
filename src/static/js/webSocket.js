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
    const wsUri = (window.location.protocol=='https:'&&'wss://'||'ws://')+window.location.host;
    conn = new WebSocket(wsUri);
    conn.onopen = function() {
        console.log("Connected");
    };
    conn.onmessage = function(e) {
        const data = JSON.parse(e.data);
        switch (data.action) {
            case "nowPlaying":
                $(".playing").removeClass("playing");
                $("#btn-music-" + data.groupIndex + "-" + data.trackListIndex).addClass("playing");
                $("#now-playing").text(`${data.groupName} > ${data.trackName}`);
                console.log("Now playing " + data.trackName + " (group " + data.groupIndex + " at index " + data.trackListIndex + ")");
                displayToast("Music", "Now playing <strong>" + data.trackName + "</strong>.");
                break;
            case "musicStopped":
                $(".playing").removeClass("playing");
                $("#now-playing").text("-");
                console.log("Music stopped playing");
                displayToast("Music", "Stopped the music.");
                break;
            case "setMusicVolume":
                $("#music-volume").slider('setValue', data.volume);
                console.log("Music volume set to " + data.volume);
                displayToast("Music", "Set volume to <strong>" + data.volume + "</strong>.");
                break;
            case "setSoundVolume":
                $("#sound-volume").slider('setValue', data.volume);
                console.log("Sound volume set to " + data.volume);
                displayToast("Sound", "Set volume to <strong>" + data.volume + "</strong>.");
                break;
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
