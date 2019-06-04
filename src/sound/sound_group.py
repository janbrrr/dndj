from typing import Dict

from src.sound.sound import Sound


class SoundGroup:
    def __init__(self, config: Dict):
        """
        Initializes a `SoundGroup` instance.

        A ``SoundGroup`` groups multiple `Sound` instances. For more information have a look at the `Sound` class.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "name": a descriptive name for the sound group
        - "directory": the directory where the files for this group are (Optional)
        - "sort": whether to sort the sounds alphabetically (Optional, default=True)
        - "sounds": a list of configs for `Sound` instances. See `Sound` class for more information

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        sounds = [Sound(sound_config) for sound_config in config["sounds"]]
        if "sort" not in config or ("sort" in config and config["sort"]):
            sounds = sorted(sounds, key=lambda x: x.name)
        self.sounds = tuple(sounds)

    def __eq__(self, other):
        if isinstance(other, SoundGroup):
            attrs_are_the_same = self.name == other.name and self.directory == other.directory
            if not attrs_are_the_same:
                return False
            if len(self.sounds) != len(other.sounds):
                return False
            for my_sound, other_sound in zip(self.sounds, other.sounds):
                if my_sound != other_sound:
                    return False
            return True
        return False
