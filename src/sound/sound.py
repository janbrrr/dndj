import random
import re
from typing import Dict

from src.sound.sound_file import SoundFile


class Sound:
    delay_single_int_regex = re.compile(r"^\d+$")
    delay_interval_regex = re.compile(r"^(\d+)-(\d+)$")

    def __init__(self, config: Dict):
        """
        Initializes a `Sound` instance.

        A ``Sound`` is not necessarily a single sound file. It is possible to specify a list of sound files. In this
        case a file will be chosen at random when the sound is being played.

        For example, you can associate four different sword sound files with a single sound named 'Sword Swing'.
        When playing this sound, a random sword sound of the provided list will be played.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "name": a descriptive name for the sound
        - "directory": the directory where the files for this sound are (Optional)
        - "volume": a value between 0 and 1 where 1 is maximum volume and 0 is no volume (Optional, default=1)
        - "repeat_count": total repeats the sound (including initial) where 0 means infinite (Optional, default=1)
        - "repeat_delay": delay in ms used when repeating. Either an int or a string '<min>-<max>' (Optional, default=0)
        - "files": a list of files (or `SoundFile` configs) associated with this sound

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        self.volume = config["volume"] if "volume" in config else 1
        self.repeat_count = int(config["repeat_count"]) if "repeat_count" in config else 1
        if "repeat_delay" in config:
            self.repeat_delay = config["repeat_delay"]
        else:
            self.repeat_delay = 0
        files = [SoundFile(sound_file) for sound_file in config["files"]]
        self.files = tuple(files)

    @property
    def repeat_delay(self) -> int:
        """
        Returns the delay used for repeating in ms. If the delay is an interval, a random number within this
        interval is returned.
        """
        if self._repeat_delay_min == self._repeat_delay_max:
            return self._repeat_delay_min
        else:
            return random.randint(self._repeat_delay_min, self._repeat_delay_max)

    @repeat_delay.setter
    def repeat_delay(self, value):
        if not isinstance(value, int) and not isinstance(value, str):
            raise ValueError("The 'repeat_delay' for a 'Sound' must be an integer or string.")
        if isinstance(value, int):
            self._repeat_delay_min = value
            self._repeat_delay_max = self._repeat_delay_min
            return
        single_number_match = self.delay_single_int_regex.match(value)
        if single_number_match is not None:
            self._repeat_delay_min = int(single_number_match.group(0))
            self._repeat_delay_max = self._repeat_delay_min
            return
        interval_match = self.delay_interval_regex.match(value)
        if interval_match is not None:
            self._repeat_delay_min = int(interval_match.group(1))
            self._repeat_delay_max = int(interval_match.group(2))
            if self._repeat_delay_max < self._repeat_delay_min:
                raise ValueError("The 'repeat_delay' cannot have a min value higher than the max value.")
            return
        raise ValueError(
            "The 'repeat_delay' for a 'Sound' must be an integer, a string of an integer or an interval in "
            "the form '<int>-<int>'."
        )

    @property
    def repeat_delay_config(self) -> str:
        """
        Returns the configuration as string for the current repeat delay.
        """
        if self._repeat_delay_min == self._repeat_delay_max:
            return str(self._repeat_delay_min)
        else:
            return f"{self._repeat_delay_min}-{self._repeat_delay_max}"

    def __eq__(self, other):
        if isinstance(other, Sound):
            attrs_are_the_same = (
                self.name == other.name
                and self.directory == other.directory
                and self.volume == other.volume
                and self.repeat_count == other.repeat_count
                and self.repeat_delay_config == other.repeat_delay_config
            )
            if not attrs_are_the_same:
                return False
            if len(self.files) != len(other.files):
                return False
            for my_file, other_file in zip(self.files, other.files):
                if my_file != other_file:
                    return False
            return True
        return False
