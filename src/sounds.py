import asyncio
import logging
import random
import os
from typing import Dict


class Sound:

    def __init__(self, config: Dict):
        """
        Initializes a `Sound` instance.

        A ``Sound`` is not necessarily a single sound file. It is possible to specify a list of sound files. In this
        case a file will be chosen at random when the sound is being played.

        For example, you can associate four different sword sound files with a single sound named 'Sword Swing'.
        When playing this sound, a random sword sound of the provided list will be played.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "name": a descriptive name for the sound
        - "files": a list of files associated with this sound

        :param config: `dict`
        """
        self.name = config["name"]
        self.files = tuple(config["files"])
        for file in self.files:
            if not file.endswith(".wav"):
                raise TypeError("Sound files must use the `.wav` format.")


class SoundGroup:

    def __init__(self, config: Dict):
        """
        Initializes a `SoundGroup` instance.

        A ``SoundGroup`` groups multiple `Sound` instances. For more information have a look at the `Sound` class.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "name": a descriptive name for the sound group
        - "directory": the directory where the files for this group are
        - "sounds": a list of configs for `Sound` instances. See `Sound` class for more information

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"]
        sounds = [Sound(sound_config) for sound_config in config["sounds"]]
        self.sounds = tuple(sounds)


class SoundManager:

    SLEEP_TIME = 0.01

    def __init__(self, config: Dict, mixer):
        """
        Initializes a `SoundManager` instance.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "volume": a value between 0 and 1 where 1 is maximum volume and 0 is no volume
        - "groups": a list of configs for `SoundGroup` instances. See `SoundGroup` class for more information

        :param config: `dict`
        :param mixer: reference to `pygame.mixer` after it has been initialized
        """
        self.mixer = mixer
        self.volume = float(config["volume"])
        groups = [SoundGroup(sound_group_config) for sound_group_config in config["groups"]]
        self.groups = tuple(groups)

    async def play_sound(self, group_index, sound_index):
        """
        Creates an asynchronous task to play the sound from the given group at the given index.
        """
        group = self.groups[group_index]
        sound = group.sounds[sound_index]
        loop = asyncio.get_event_loop()
        playing = loop.create_task(self._play_sound(group, sound))
        await asyncio.sleep(self.SLEEP_TIME)  # Return to the event loop that will start the task

    async def _play_sound(self, group: SoundGroup, sound: Sound):
        """
        Plays the given sound.
        """
        logging.debug(f"Loading '{sound.name}'")
        file = random.choice(sound.files)
        sound = self.mixer.Sound(os.path.join(group.directory, file))
        sound.set_volume(self.volume)
        sound.play()
        logging.info(f"Now Playing: {file}")
        await asyncio.sleep(sound.get_length())
        logging.info(f"Finished playing: {file}")

    def set_volume(self, volume):
        """
        Sets the volume for the sounds.

        :param volume: new volume, a value between 0 (mute) and 1 (max)
        """
        self.volume = volume
        logging.debug(f"Changed sound volume to {volume}")
