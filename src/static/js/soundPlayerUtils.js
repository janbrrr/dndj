// Selector functions

function selectSoundMasterVolumeSlider() {
    return $("#sound-master-volume");
}

function selectSoundGroupHeader(groupIndex) {
    return $("#sound-group-header-" + groupIndex);
}

function selectSoundContainer(groupIndex, soundIndex) {
    return $("#sound-" + groupIndex + "-" + soundIndex);
}

function selectSoundVolumeSlider(groupIndex, soundIndex) {
    return $("#sound-volume-" + groupIndex + "-" + soundIndex);
}

function selectSoundRepeatCountInput(groupIndex, soundIndex) {
    return $("#sound-repeat-count-input-" + groupIndex + "-" + soundIndex);
}

function selectSoundLoopDelayInput(groupIndex, soundIndex) {
    return $("#sound-loop-delay-input-" + groupIndex + "-" + soundIndex);
}

// Utility functions

function setSoundMasterVolume(volume) {
    selectSoundMasterVolumeSlider().slider('setValue', volume);
}

function setSoundVolume(groupIndex, soundIndex, volume) {
    selectSoundVolumeSlider(groupIndex, soundIndex).slider('setValue', volume);
}

function setSoundPlaying(groupIndex, soundIndex) {
    selectSoundGroupHeader(groupIndex).addClass("playing");
    selectSoundContainer(groupIndex, soundIndex).addClass("playing");
}

function setSoundNotPlaying(groupIndex, soundIndex) {
    selectSoundContainer(groupIndex, soundIndex).removeClass("playing");
    const groupContainer = selectSoundGroupHeader(groupIndex).parent();
    if (groupContainer.find(".group-item.playing").length === 0) {
        groupContainer.find(".group-header").removeClass("playing");
    }
}

function setSoundRepeatCount(groupIndex, soundIndex, repeatCount) {
    selectSoundRepeatCountInput(groupIndex, soundIndex).val(repeatCount);
}

function setSoundLoopDelay(groupIndex, soundIndex, loopDelay) {
    selectSoundLoopDelayInput(groupIndex, soundIndex).val(loopDelay);
}
