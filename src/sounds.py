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


class SoundManager:

    SLEEP_TIME = 0.01

    def __init__(self, config_dict: Dict, mixer):
        """
        Initializes a `SoundManager` instance.

        The `config_dict` parameter is expected to be a dictionary with the following keys:
        - "volume": a value between 0 and 1 where 1 is maximum volume and 0 is no volume
        - "directory": the directory where the files are
        - "sounds": a list of sound configs. See `Sound` class for more information

        :param config_dict: `dict`
        :param mixer: reference to `pygame.mixer` after it has been initialized
        """
        self.mixer = mixer
        self.volume = float(config_dict["volume"])
        self.directory = config_dict["directory"]
        sounds = [Sound(sound_config) for sound_config in config_dict["sounds"]]
        self.sounds = tuple(sounds)

    async def play_sound(self, index):
        """
        Creates an asynchronous task to play the sound at the given index.
        """
        sound = self.sounds[index]
        loop = asyncio.get_event_loop()
        playing = loop.create_task(self._play_sound(sound))
        await asyncio.sleep(self.SLEEP_TIME)  # Return to the event loop that will start the task

    async def _play_sound(self, sound: Sound):
        """
        Plays the given sound.
        """
        logging.debug(f"Loading '{sound.name}'")
        file = random.choice(sound.files)
        sound = self.mixer.Sound(os.path.join(self.directory, file))
        sound.play()
        logging.info(f"Now Playing: {file}")
        await asyncio.sleep(sound.get_length())
        logging.info(f"Finished playing: {file}")
