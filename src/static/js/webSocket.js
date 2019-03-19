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
                $("#music-" + data.groupIndex + "-" + data.trackListIndex).addClass("playing");
                console.log("Now playing from group " + data.groupIndex + " at index " + data.trackListIndex);
                break;
            case "musicStopped":
                $(".playing").removeClass("playing");
                console.log("Music stopped playing");
                break;
            case "setMusicVolume":
                $("#music-volume").val(data.volume);
                console.log("Music volume set to " + data.volume);
                break;
            case "setSoundVolume":
                $("#sound-volume").val(data.volume);
                console.log("Sound volume set to " + data.volume);
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
