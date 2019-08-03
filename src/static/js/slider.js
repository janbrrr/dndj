$(document).ready(function() {
    const musicMasterVolume = $("#music-master-volume");
    musicMasterVolume.slider({});
    musicMasterVolume.on("slideStop", function(slideEvt) {
        setMusicMasterVolume(slideEvt.value);
    });

    const musicVolume = $(".music-volume");
    musicVolume.slider({});
    musicVolume.on("slideStop", function(slideEvt) {
        const target = $(slideEvt.currentTarget);
        const groupIndex = target.data("group-index");
        const trackListIndex = target.data("track-list-index");
        setMusicVolume(groupIndex, trackListIndex, slideEvt.value);
    });

    const soundMasterVolume = $("#sound-master-volume");
    soundMasterVolume.slider({});
    soundMasterVolume.on("slideStop", function(slideEvt) {
        setSoundMasterVolume(slideEvt.value);
    });

    const soundVolume = $(".sound-volume");
    soundVolume.slider({});
    soundVolume.on("slideStop", function(slideEvt) {
        const target = $(slideEvt.currentTarget);
        const groupIndex = target.data("group-index");
        const soundIndex = target.data("sound-index");
        setSoundVolume(groupIndex, soundIndex, slideEvt.value);
    });
});