import asyncio
import logging
import os
import random
from typing import Callable, Dict, List

import pygame.mixer
from aiohttp.web_request import Request

from src.sound import utils
from src.sound.sound_actions import SoundActions
from src.sound.sound_callback_handler import SoundCallbackHandler
from src.sound.sound_callback_info import SoundCallbackInfo
from src.sound.sound_checker import SoundChecker
from src.sound.sound_group import SoundGroup
from src.sound.sound_tracker import SoundTracker


logger = logging.getLogger(__name__)


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
        - "master_volume": float (0 to 1)

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
        self.callback_handler = SoundCallbackHandler(callback_fn=callback_fn)
        self.tracker = SoundTracker()
        self.players = {}
        SoundChecker().do_all_checks(self.groups, self.directory)

    def _get_player_key(self, group_index: int, sound_index: int):
        """
        Returns the dictionary key for the dictionary of player instances at `self.players`.
        """
        return f"{group_index}-{sound_index}"

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
            sounds_being_played.append(
                SoundCallbackInfo(group_index, group.name, sound_index, sound.name, sound.volume, sound.loop)
            )
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
        task = loop.create_task(self._play_repeating_sound(request, group_index, sound_index))
        self.tracker.register_sound(group_index, sound_index, task)
        await asyncio.sleep(self.SLEEP_TIME)  # Return to the event loop that will start the task

    async def _play_repeating_sound(self, request: Request, group_index: int, sound_index: int):
        """
        Plays the given sound. Repeats the sound if its `loop` attribute is set.
        """
        group = self.groups[group_index]
        sound = group.sounds[sound_index]
        while True:
            await self._play_sound(request, group_index, sound_index)
            if not sound.loop:
                break

    async def _play_sound(self, request: Request, group_index: int, sound_index: int):
        """
        Plays the given sound.
        """
        group = self.groups[group_index]
        sound = group.sounds[sound_index]
        sound_info = SoundCallbackInfo(group_index, group.name, sound_index, sound.name, sound.volume, sound.loop)
        try:
            logger.debug(f"Loading '{sound.name}'")
            await self.callback_handler(SoundActions.START, request, sound_info, self.volume)
            logger.info(f"Now Playing: {sound.name}")
            await self._play_sound_file(group_index, sound_index)
            await self.callback_handler(SoundActions.FINISH, request, sound_info, self.volume)
            logger.info(f"Finished playing: {sound.name}")
        except asyncio.CancelledError:
            logger.info(f"Cancelled: {sound.name}")
            await self.callback_handler(SoundActions.STOP, request, sound_info, self.volume)
            raise

    async def _play_sound_file(self, group_index: int, sound_index: int):
        """
        Plays a sound file from the given group and sound.
        """
        group = self.groups[group_index]
        sound = group.sounds[sound_index]
        root_directory = utils.get_sound_root_directory(group, sound, default_dir=self.directory)
        sound_file = random.choice(sound.files)
        pygame_sound = None
        try:
            pygame_sound = pygame.mixer.Sound(os.path.join(root_directory, sound_file.file))
            self.players[self._get_player_key(group_index, sound_index)] = pygame_sound
            pygame_sound.set_volume(self.volume * sound.volume)
            if sound_file.end_at is not None:
                pygame_sound.play(maxtime=sound_file.end_at)
                await asyncio.sleep(sound_file.end_at / 1000)
            else:
                pygame_sound.play()
                await asyncio.sleep(pygame_sound.get_length())
        except asyncio.CancelledError:
            if pygame_sound is not None:
                pygame_sound.stop()
                del self.players[self._get_player_key(group_index, sound_index)]
                raise

    async def set_master_volume(self, request: Request, volume: float):
        """
        Sets the master volume for the sounds.

        :param request: the request that caused this action
        :param volume: new volume, a value between 0 (mute) and 1 (max)
        """
        self.volume = volume
        logger.debug(f"Changed sound master volume to {volume}")
        await self.callback_handler(SoundActions.MASTER_VOLUME, request, None, self.volume)

    async def set_sound_volume(self, request: Request, group_index: int, sound_index: int, volume: float):
        """
        Sets the volume for a specific sound. If the sound is currently being played, the volume of the player is
        updated.

        :param request: the request that caused this action
        :param group_index: index of the group of the sound
        :param sound_index: index of the sound in the group
        :param volume: new volume, a value between 0 (mute) and 1 (max)
        """
        group = self.groups[group_index]
        sound = group.sounds[sound_index]
        sound.volume = volume
        sound_info = SoundCallbackInfo(group_index, group.name, sound_index, sound.name, sound.volume, sound.loop)
        player_key = self._get_player_key(group_index, sound_index)
        if player_key in self.players:
            self.players[player_key].set_volume(self.volume * sound.volume)
        logger.debug(f"Changed sound volume for group={group_index}, sound={sound_index} to {volume}")
        await self.callback_handler(SoundActions.VOLUME, request, sound_info, self.volume)

    async def set_sound_loop(self, request: Request, group_index: int, sound_index: int, loop_value: bool):
        """
        Sets the loop attribute for a specific sound.

        :param request: the request that caused this action
        :param group_index: index of the group of the sound
        :param sound_index: index of the sound in the group
        :param loop_value: new value of the loop attribute
        """
        group = self.groups[group_index]
        sound = group.sounds[sound_index]
        sound.loop = loop_value
        sound_info = SoundCallbackInfo(group_index, group.name, sound_index, sound.name, sound.volume, sound.loop)
        logger.debug(f"Changed sound loop attribute for group={group_index}, sound={sound_index} to {loop_value}")
        await self.callback_handler(SoundActions.LOOP, request, sound_info, self.volume)

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
