// Selector functions

function selectPlayingInMusicTab() {
    return $("#music .playing");
}

function selectMusicOverview() {
    return $("#now-playing");
}

function selectMusicMasterVolumeSlider() {
    return $("#music-master-volume");
}

function selectMusicGroupContainer(groupIndex) {
    return $("#music-group-" + groupIndex);
}

function selectTrackListContainer(groupIndex, trackListIndex) {
    return $("#track-list-" + groupIndex + "-" + trackListIndex);
}

function selectTrackListVolumeSlider(groupIndex, trackListIndex) {
    return $("#track-list-volume-" + groupIndex + "-" + trackListIndex);
}

// Utility functions

function setMusicNotPlaying() {
    selectPlayingInMusicTab().removeClass("playing");
    selectMusicOverview().text("-");
}

function setMusicPlaying(groupIndex, groupName, trackListIndex, trackName) {
    setMusicNotPlaying();
    selectMusicGroupContainer(groupIndex).addClass("playing");
    selectTrackListContainer(groupIndex, trackListIndex).addClass("playing");
    selectMusicOverview().text(`${groupName} > ${trackName}`);
}

function setMusicMasterVolume(volume) {
    selectMusicMasterVolumeSlider().slider('setValue', volume);
}

function setTrackListVolumeSlider(groupIndex, trackListIndex, volume) {
    selectTrackListVolumeSlider(groupIndex, trackListIndex).slider('setValue', volume);
}