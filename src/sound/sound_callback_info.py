from collections import namedtuple


SoundCallbackInfo = namedtuple(
    "SoundCallbackInfo",
    ["group_index", "group_name", "sound_index", "sound_name", "volume", "repeat_count", "repeat_delay_config"],
)
