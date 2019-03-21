$(document).ready(function() {
    const musicVolume = $("#music-volume");
    musicVolume.slider({});
    musicVolume.on("slideStop", function(slideEvt) {
        setMusicVolume(slideEvt.value);
    });

    const soundVolume = $("#sound-volume");
    soundVolume.slider({});
    soundVolume.on("slideStop", function(slideEvt) {
        setSoundVolume(slideEvt.value);
    });
});