import asyncio
import logging
from collections import namedtuple
from typing import Callable, Dict

import vlc
from aiohttp.web_request import Request

from src.music import utils
from src.music.music_actions import MusicActions
from src.music.music_callback_handler import MusicCallbackHandler
from src.music.music_callback_info import MusicCallbackInfo
from src.music.music_checker import MusicChecker
from src.music.music_group import MusicGroup
from src.music.track import Track
from src.music.track_list import TrackList


logger = logging.getLogger(__name__)

CurrentlyPlaying = namedtuple("CurrentlyPlaying", ["group_index", "track_list_index", "task"])


class MusicManager:

    SLEEP_TIME = 0.01
    VALID_YOUTUBE_TRACKS_CACHE = "valid_youtube_tracks.json"

    def __init__(self, config: Dict, callback_fn: Callable[[MusicActions, Request, MusicCallbackInfo], None] = None):
        """
        Initializes a `MusicManager` instance.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "volume": an integer between 0 (mute) and 100 (max)
        - "directory": the default directory to use if no directory is further specified (Optional)
        - "sort": whether to sort the groups alphabetically (Optional, default=True)
        - "groups": a list of configs for `MusicGroup` instances. See `MusicGroup` class for more information

        The `callback_fn` is an async function that should accept the following arguments:
        - "action": value of type `MusicActions`
        - "request": the request that caused the action
        - "music_info": an instance of `MusicCallbackInfo` (fields are `None` if nothing is being played)

        :param config: `dict`
        :param callback_fn: function to call when the active music changes
        """
        self.volume = int(config["volume"])
        self.directory = config["directory"] if "directory" in config else None
        groups = [MusicGroup(group_config) for group_config in config["groups"]]
        if "sort" not in config or ("sort" in config and config["sort"]):
            groups = sorted(groups, key=lambda x: x.name)
        self.groups = tuple(groups)
        self._currently_playing = None
        self._current_player = None
        self.callback_handler = MusicCallbackHandler(callback_fn=callback_fn)
        MusicChecker().do_all_checks(self.groups, self.directory)

    def __eq__(self, other):
        if isinstance(other, MusicManager):
            attrs_are_the_same = (
                self.volume == other.volume
                and self.directory == other.directory
                and self._currently_playing == other._currently_playing
            )
            if not attrs_are_the_same:
                return False
            if len(self.groups) != len(other.groups):
                return False
            for my_group, other_group in zip(self.groups, other.groups):
                if my_group != other_group:
                    return False
            return True
        return False

    @property
    def currently_playing(self) -> MusicCallbackInfo:
        """
        Returns information about the music that is currently being played.
        Fields are `None` if nothing is being played.
        """
        if self._currently_playing is not None:
            group_index = self._currently_playing.group_index
            group = self.groups[group_index]
            track_list_index = self._currently_playing.track_list_index
            track_list = group.track_lists[track_list_index]
            return MusicCallbackInfo(group_index, group.name, track_list_index, track_list.name, self.volume)
        return MusicCallbackInfo(None, None, None, None, self.volume)

    async def cancel(self):
        """
        If a track is currently being played, the replay will be cancelled.
        """
        if self._currently_playing is not None:
            self._currently_playing.task.cancel()
            while self._currently_playing is not None:  # wait till track list finishes cancelling
                await asyncio.sleep(self.SLEEP_TIME)

    async def play_track_list(self, request, group_index, track_list_index):
        """
        Creates an asynchronous task to play the track list at the given index.
        If a track list is already being played, it will be cancelled and the new track list will be played.
        """
        logger.debug(f"Received request to play music from group {group_index} at index " f"{track_list_index}")
        await self.cancel()
        loop = asyncio.get_event_loop()
        self._currently_playing = CurrentlyPlaying(
            group_index,
            track_list_index,
            loop.create_task(self._play_track_list(request, group_index, track_list_index)),
        )
        logger.debug(f"Created a task to play music from group {group_index} at index " f"{track_list_index}")
        await asyncio.sleep(self.SLEEP_TIME)  # Return to the event loop that will start the task

    async def _play_track_list(self, request, group_index, track_list_index):
        """
        Plays the given track list from the given group.
        """
        group = self.groups[group_index]
        track_list = group.track_lists[track_list_index]
        cancelled = False
        try:
            logger.info(f"Loading '{track_list.name}'")
            await self.callback_handler(action=MusicActions.START, request=request, music_info=self.currently_playing)
            while True:
                for track in track_list.tracks:
                    await self._play_track(group, track_list, track)
                if not track_list.loop:
                    break
            logger.info(f"Finished '{track_list.name}'")
            await self.callback_handler(action=MusicActions.FINISH, request=request, music_info=self.currently_playing)
        except asyncio.CancelledError:
            logger.info(f"Cancelled '{track_list.name}'")
            await self.callback_handler(action=MusicActions.STOP, request=request, music_info=self.currently_playing)
            cancelled = True
            raise
        finally:
            if self._current_player is not None:
                self._current_player.stop()
            self._currently_playing = None
            self._current_player = None
            if not cancelled and track_list.next is not None:
                await self._play_next_track_list(request, track_list)

    async def _play_track(self, group: MusicGroup, track_list: TrackList, track: Track):
        """
        Plays the given track from the given track list and group.
        """
        try:
            path = utils.get_track_path(group, track_list, track, default_dir=self.directory)
        except ValueError:
            logger.error(f"Failed to play '{track.file}'.")
            raise asyncio.CancelledError()
        self._current_player = vlc.MediaPlayer(vlc.Instance("--novideo"), path)
        self._current_player.audio_set_volume(0)
        success = self._current_player.play()
        if success == -1:
            logger.error(f"Failed to play {path}")
            raise asyncio.CancelledError
        if track.start_at is not None:
            self._current_player.set_time(track.start_at)
        logger.info(f"Now Playing: {track.file}")
        await self._wait_for_current_player_to_be_playing()
        await self._set_volume(self.volume, set_global=False)
        while self._current_player.is_playing():
            try:
                if track.end_at is not None and self._current_player.get_time() >= track.end_at:
                    self._current_player.stop()
                await asyncio.sleep(self.SLEEP_TIME)
            except asyncio.CancelledError:
                logger.debug(f"Received cancellation request for {track.file}")
                await self._set_volume(0, set_global=False)
                raise
        logger.info(f"Finished playing: {track.file}")

    async def _wait_for_current_player_to_be_playing(self):
        """
        Waits until the `current_player` is playing.
        """
        if self._current_player is not None:
            while not self._current_player.is_playing():
                await asyncio.sleep(self.SLEEP_TIME)

    async def _play_next_track_list(self, request, current_track_list: TrackList):
        """
        If there is a next track list to play (`track_list.next` is set), then create a task to play it.
        """
        if current_track_list.next is None:
            return
        next_group_index = None
        next_track_list_index = None
        for _group_index, _group in enumerate(self.groups):
            for _track_list_index, _track_list in enumerate(_group.track_lists):
                if _track_list.name == current_track_list.next:
                    next_group_index = _group_index
                    next_track_list_index = _track_list_index
                    break
        if next_group_index is None or next_track_list_index is None:
            logger.error(f"Could not find a track list named '{current_track_list.name}'")
        else:
            await self.play_track_list(request, next_group_index, next_track_list_index)

    async def set_volume(self, request, volume, seconds=1):
        """
        Sets the volume for the music.
        """
        await self._set_volume(volume, set_global=True, seconds=seconds)
        await self.callback_handler(action=MusicActions.VOLUME, request=request, music_info=self.currently_playing)

    async def _set_volume(self, volume, set_global=True, smooth=True, n_steps=20, seconds=2):
        """
        Sets the volume for the music.

        :param volume: new volume, a value between 0 (mute) and 100 (max)
        :param set_global: whether to set this as the new global volume
        :param smooth: whether to do a smooth transitions
        :param n_steps: how many steps the transitions incorporates
        :param seconds: the time in which the transitions takes place
        """
        if self._current_player is not None:
            if not smooth:
                self._current_player.audio_set_volume(volume)
            else:
                current_volume = self._current_player.audio_get_volume()
                step_size = (current_volume - volume) / n_steps
                for i in range(n_steps):
                    new_volume = int(current_volume - (i + 1) * step_size)
                    self._current_player.audio_set_volume(new_volume)
                    await asyncio.sleep(seconds / n_steps)
        if set_global:
            self.volume = volume
            logger.debug(f"Changed music volume to {volume}")
