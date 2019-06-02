import asyncio
import logging
import random
import os

import pygame.mixer
from typing import Dict, Callable, List

from aiohttp.web_request import Request

from src.sound import SoundFile
from src.sound.sound import Sound
from src.sound.sound_actions import SoundActions
from src.sound.sound_callback_handler import SoundCallbackHandler
from src.sound.sound_callback_info import SoundCallbackInfo
from src.sound.sound_group import SoundGroup
from src.sound.sound_tracker import SoundTracker


class SoundManager:

    SLEEP_TIME = 0.01

    def __init__(self, config: Dict, callback_fn: Callable = None):
        """
        Initializes a `SoundManager` instance.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "volume": a value between 0 and 1 where 1 is maximum volume and 0 is no volume
        - "directory": the default directory to use if no directory is further specified (Optional)
        - "sort": whether to sort the groups alphabetically (Optional, default=True)
        - "groups": a list of configs for `SoundGroup` instances. See `SoundGroup` class for more information

        The `callback_fn` is an async function that should accept the following optional keyword arguments:
        - "action": value of type `SoundActions`
        - "request": the request that caused the action
        - "sound_info": instance of type `SoundCallbackInfo` (`None` if action not related to particular sound)

        :param config: `dict`
        :param callback_fn: function to call when the active sounds change
        """
        pygame.mixer.init()
        self.volume = float(config["volume"])
        self.directory = config["directory"] if "directory" in config else None
        groups = [SoundGroup(sound_group_config) for sound_group_config in config["groups"]]
        if "sort" not in config or ("sort" in config and config["sort"]):
            groups = sorted(groups, key=lambda x: x.name)
        self.groups = tuple(groups)
        self._check_sounds_are_valid()
        self.callback_handler = SoundCallbackHandler(callback_fn=callback_fn)
        self.tracker = SoundTracker()

    def _check_sounds_are_valid(self):
        """
        Iterates through every sound file and attempts to get its path. Logs any error and raises a `ValueError`
        if a file path is invalid.
        """
        logging.info("Checking that sounds point to valid paths...")
        for group in self.groups:
            for sound in group.sounds:
                try:
                    root_directory = self._get_sound_root_directory(group, sound)
                except ValueError as ex:
                    logging.error(f"Sound '{sound.name}' is missing the directory.")
                    raise ex
                for sound_file in sound.files:
                    file_path = os.path.join(root_directory, sound_file.file)
                    if not os.path.isfile(file_path):
                        logging.error(f"File {file_path} does not exist")
                        raise ValueError
        logging.info("Success! All sounds point to valid paths.")

    @property
    def currently_playing(self) -> List[SoundCallbackInfo]:
        """
        Returns a list of the sounds that are currently being played.
        """
        active_sounds = self.tracker.active_sounds
        sounds_being_played = []
        for active_sound in active_sounds:
            group_index = active_sound.group_index
            group = self.groups[group_index]
            sound_index = active_sound.sound_index
            sound = group.sounds[sound_index]
            sounds_being_played.append(SoundCallbackInfo(group_index, group.name, sound_index, sound.name))
        return sounds_being_played

    async def cancel_sound(self, group_index: int, sound_index: int):
        """
        If the sound is currently being played, the replay will be cancelled.
        """
        await self.tracker.cancel_sound(group_index, sound_index)

    async def play_sound(self, request: Request, group_index: int, sound_index: int):
        """
        Creates an asynchronous task to play the sound from the given group at the given index.
        If the sound is already being played, it will be cancelled and restarted.
        """
        await self.cancel_sound(group_index, sound_index)
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._play_sound(request, group_index, sound_index))
        self.tracker.register_sound(group_index, sound_index, task)
        await asyncio.sleep(self.SLEEP_TIME)  # Return to the event loop that will start the task

    async def _play_sound(self, request: Request, group_index: int, sound_index: int):
        """
        Plays the given sound.
        """
        group = self.groups[group_index]
        sound = group.sounds[sound_index]
        sound_info = SoundCallbackInfo(group_index, group.name, sound_index, sound.name)
        try:
            logging.debug(f"Loading '{sound.name}'")
            sound_file = random.choice(sound.files)
            root_directory = self._get_sound_root_directory(group, sound)
            await self.callback_handler(action=SoundActions.START, request=request, sound_info=sound_info)
            logging.info(f"Now Playing: {sound.name}")
            await self._play_sound_file(root_directory, sound_file)
            await self.callback_handler(action=SoundActions.FINISH, request=request, sound_info=sound_info)
            logging.info(f"Finished playing: {sound.name}")
        except asyncio.CancelledError:
            logging.info(f"Cancelled: {sound.name}")
            await self.callback_handler(action=SoundActions.STOP, request=request, sound_info=sound_info)
            raise

    async def _play_sound_file(self, root_directory: str, sound_file: SoundFile):
        """
        Plays the given sound file.
        """
        pygame_sound = None
        try:
            pygame_sound = pygame.mixer.Sound(os.path.join(root_directory, sound_file.file))
            pygame_sound.set_volume(self.volume)
            if sound_file.end_at is not None:
                pygame_sound.play(maxtime=sound_file.end_at)
                await asyncio.sleep(sound_file.end_at / 1000)
            else:
                pygame_sound.play()
                await asyncio.sleep(pygame_sound.get_length())
        except asyncio.CancelledError:
            if pygame_sound is not None:
                pygame_sound.stop()
                raise

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
            raise ValueError(f"Sound '{sound.name}' is missing directory.")
        return root_directory

    def set_volume(self, volume):
        """
        Sets the volume for the sounds.

        :param volume: new volume, a value between 0 (mute) and 1 (max)
        """
        self.volume = volume
        logging.debug(f"Changed sound volume to {volume}")

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
