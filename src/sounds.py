import asyncio
import logging
import random
import os
import time
import pygame.mixer
from typing import Dict, Union


class SoundFile:

    def __init__(self, config: Union[str, Dict]):
        """
        Initializes a `SoundFile` instance.

        The `config` parameter is either a `str` containing the filename or a dictionary with the following keys:
        - "file": the filename
        - "end_at": time at which the sound should end in the %H:%M:%S format (Optional)

        :param config: String containing the filename or a dictionary containing the config
        """
        if isinstance(config, str):
            self.file = config
            self.end_at = None
        else:
            self.file = config["file"]
            end_at = config["end_at"] if "end_at" in config else None
            if end_at is not None:
                time_struct = time.strptime(end_at, "%H:%M:%S")
                self.end_at = (time_struct.tm_sec + time_struct.tm_min * 60 + time_struct.tm_hour * 60 * 60) \
                              * 1000  # in ms
            else:
                self.end_at = None
        if not self.file.endswith(".wav") and not self.file.endswith(".ogg"):
            raise TypeError("Sound files must use the `.wav` or `.ogg` format.")

    def __eq__(self, other):
        if isinstance(other, SoundFile):
            return self.file == other.file and self.end_at == other.end_at
        return False


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
        - "directory": the directory where the files for this sound are (Optional)
        - "files": a list of files (or `SoundFile` configs) associated with this sound

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        files = [SoundFile(sound_file) for sound_file in config["files"]]
        self.files = tuple(files)

    def __eq__(self, other):
        if isinstance(other, Sound):
            attrs_are_the_same = self.name == other.name and self.directory == other.directory
            if not attrs_are_the_same:
                return False
            if len(self.files) != len(other.files):
                return False
            for my_file, other_file in zip(self.files, other.files):
                if my_file != other_file:
                    return False
            return True
        return False


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


class SoundManager:
    SLEEP_TIME = 0.01

    def __init__(self, config: Dict):
        """
        Initializes a `SoundManager` instance.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "volume": a value between 0 and 1 where 1 is maximum volume and 0 is no volume
        - "directory": the default directory to use if no directory is further specified (Optional)
        - "sort": whether to sort the groups alphabetically (Optional, default=True)
        - "groups": a list of configs for `SoundGroup` instances. See `SoundGroup` class for more information

        :param config: `dict`
        """
        pygame.mixer.init()
        self.volume = float(config["volume"])
        self.directory = config["directory"] if "directory" in config else None
        groups = [SoundGroup(sound_group_config) for sound_group_config in config["groups"]]
        if "sort" not in config or ("sort" in config and config["sort"]):
            groups = sorted(groups, key=lambda x: x.name)
        self.groups = tuple(groups)

    def __eq__(self, other):
        if isinstance(other, SoundManager):
            attrs_are_the_same = self.volume == other.volume and self.directory == other.directory
            if not attrs_are_the_same:
                return False
            if len(self.groups) != len(other.groups):
                return False
            for my_group, other_group in zip(self.groups, other.groups):
                if my_group != other_group:
                    return False
            return True
        return False

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
        sound_file = random.choice(sound.files)
        try:
            root_directory = self._get_sound_root_directory(group, sound)
        except ValueError:
            logging.error(f"Failed to play '{sound.name}'. "
                          f"You have to specify the directory on either the global level, group level or sound level.")
            return
        pygame_sound = pygame.mixer.Sound(os.path.join(root_directory, sound_file.file))
        pygame_sound.set_volume(self.volume)
        if sound_file.end_at is not None:
            pygame_sound.play(maxtime=sound_file.end_at)
            logging.info(f"Now Playing: {sound.name}")
            await asyncio.sleep(sound_file.end_at / 1000)
        else:
            pygame_sound.play()
            logging.info(f"Now Playing: {sound.name}")
            await asyncio.sleep(pygame_sound.get_length())
        logging.info(f"Finished playing: {sound.name}")

    def _get_sound_root_directory(self, group: SoundGroup, sound: Sound) -> str:
        """
        Returns the root directory of the sound.

        Lookup order:
        1. the directory specified directly on the sound
        2. the directory specified on the group
        3. the global directory specified

        If none of the above exists, raise a ValueError.
        """
        root_directory = sound.directory if sound.directory is not None else group.directory
        root_directory = root_directory if root_directory is not None else self.directory
        if root_directory is None:
            raise ValueError("Missing directory")
        return root_directory

    def set_volume(self, volume):
        """
        Sets the volume for the sounds.

        :param volume: new volume, a value between 0 (mute) and 1 (max)
        """
        self.volume = volume
        logging.debug(f"Changed sound volume to {volume}")
