import vlc
import pafy
import asyncio
import logging
import os
from collections import namedtuple
from typing import Dict, Callable, Union
from enum import Enum

from src.music.music_group import MusicGroup
from src.music.track import Track
from src.music.track_list import TrackList

CurrentlyPlaying = namedtuple("CurrentlyPlaying", ["group_index", "track_list_index", "task"])

MusicInformation = namedtuple("MusicInformation", ["group_index", "group_name", "track_list_index", "track_list_name"])


class MusicManagerAction(Enum):
    START = 1
    STOP = 2
    FINISH = 3


class MusicManager:

    SLEEP_TIME = 0.01

    def __init__(self, config: Dict, on_music_changes_callback: Callable = None):
        """
        Initializes a `MusicManager` instance.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "volume": an integer between 0 (mute) and 100 (max)
        - "directory": the default directory to use if no directory is further specified (Optional)
        - "sort": whether to sort the groups alphabetically (Optional, default=True)
        - "groups": a list of configs for `MusicGroup` instances. See `MusicGroup` class for more information

        The `on_music_change_callback` is an async function that should accept the following optional keyword arguments:
        - "action": value of type `MusicManagerAction`
        - "request": the request that caused the action
        - "currently_playing": an instance of `CurrentlyPlaying` (`None` if nothing is being played)

        :param config: `dict`
        :param on_music_changes_callback: function to call when the active music changes
        """
        self.volume = int(config["volume"])
        self.directory = config["directory"] if "directory" in config else None
        groups = [MusicGroup(group_config) for group_config in config["groups"]]
        if "sort" not in config or ("sort" in config and config["sort"]):
            groups = sorted(groups, key=lambda x: x.name)
        self.groups = tuple(groups)
        self._currently_playing = None
        self._current_player = None
        self.on_music_changes_callback = on_music_changes_callback

    def __eq__(self, other):
        if isinstance(other, MusicManager):
            attrs_are_the_same = self.volume == other.volume \
                                 and self.directory == other.directory \
                                 and self._currently_playing == other._currently_playing
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
    def currently_playing(self) -> Union[None, MusicInformation]:
        """
        Returns information about the music that is currently being played. Returns `None` if nothing is being played.
        """
        if self._currently_playing is not None:
            group_index = self._currently_playing.group_index
            group = self.groups[group_index]
            track_list_index = self._currently_playing.track_list_index
            track_list = group.track_lists[track_list_index]
            return MusicInformation(group_index, group.name, track_list_index, track_list.name)
        return None

    async def cancel(self, request, use_callback=True):
        """
        If a track is currently being played, the replay will be cancelled.
        """
        if self._currently_playing is not None:
            self._currently_playing.task.cancel()
            while self._currently_playing is not None:  # wait till track list finishes cancelling
                await asyncio.sleep(self.SLEEP_TIME)
        if self.on_music_changes_callback is not None and use_callback:
            await self.on_music_changes_callback(action=MusicManagerAction.STOP, request=request,
                                                 currently_playing=None)

    async def play_track_list(self, request, group_index, track_list_index):
        """
        Creates an asynchronous task to play the track list at the given index.
        If a track list is already being played, it will be cancelled and the new track list will be played.
        """
        logging.debug(f"Received request to play music from group {group_index} at index "
                      f"{track_list_index}")
        await self.cancel(request, use_callback=False)
        loop = asyncio.get_event_loop()
        self._currently_playing = CurrentlyPlaying(group_index, track_list_index,
                                                   loop.create_task(self._play_track_list(request, group_index,
                                                                                          track_list_index)))
        logging.debug(f"Created a task to play music from group {group_index} at index "
                      f"{track_list_index}")
        await asyncio.sleep(self.SLEEP_TIME)  # Return to the event loop that will start the task

    async def _play_track_list(self, request, group_index, track_list_index):
        """
        Plays the given track list from the given group.
        """
        group = self.groups[group_index]
        track_list = group.track_lists[track_list_index]
        try:
            logging.info(f"Loading '{track_list.name}'")
            if self.on_music_changes_callback is not None:
                await self.on_music_changes_callback(action=MusicManagerAction.START, request=request,
                                                     currently_playing=self.currently_playing)
            while True:
                for track in track_list.tracks:
                    await self._play_track(group, track_list, track)
                if not track_list.loop:
                    break
            if self.on_music_changes_callback is not None:
                await self.on_music_changes_callback(action=MusicManagerAction.FINISH, request=request,
                                                     currently_playing=None)
        except asyncio.CancelledError:
            logging.info(f"Cancelled '{track_list.name}'")
            raise
        finally:
            if self._current_player is not None:
                self._current_player.stop()
            self._currently_playing = None
            self._current_player = None

    async def _play_track(self, group: MusicGroup, track_list: TrackList, track: Track):
        """
        Plays the given track from the given track list and group.
        """
        try:
            path = self._get_track_path(group, track_list, track)
        except ValueError:
            logging.error(f"Failed to play '{track.file}'.")
            raise asyncio.CancelledError()
        self._current_player = vlc.MediaPlayer(vlc.Instance(), path)
        self._current_player.audio_set_volume(0)
        success = self._current_player.play()
        if success == -1:
            logging.error(f"Failed to play {path}")
            raise asyncio.CancelledError
        if track.start_at is not None:
            self._current_player.set_time(track.start_at)
        logging.info(f"Now Playing: {track.file}")
        await self._wait_for_current_player_to_be_playing()
        await self.set_volume(self.volume, set_global=False)
        while self._current_player.is_playing():
            try:
                if track.end_at is not None and self._current_player.get_time() >= track.end_at:
                    self._current_player.stop()
                await asyncio.sleep(self.SLEEP_TIME)
            except asyncio.CancelledError:
                logging.debug(f"Received cancellation request for {track.file}")
                await self.set_volume(0, set_global=False)
                raise
        logging.info(f"Finished playing: {track.file}")

    def _get_track_path(self, group: MusicGroup, track_list: TrackList, track: Track) -> str:
        """
        Returns the path of the `Track` instance that should be played.

        If the `file` attribute is a link to a YouTube video, get the corresponding
        URL for the best audio stream and return it.

        Otherwise assume that the `file` attribute refers to a file location. Return the file path.
        Raises a `ValueError` if the file path is not valid.

        :param group: `MusicGroup` where the `track_list` is in
        :param track_list: `TrackList` where the `track` is in
        :param track: the `Track` instance that should be played
        :return: path to the `track` location that the VLC player can understand
        """
        if track.is_youtube_link:
            youtube_video = pafy.new(track.file)
            best_audio_stream = youtube_video.getbestaudio()
            return best_audio_stream.url
        else:  # is regular file
            try:
                root_directory = self._get_track_list_root_directory(group, track_list)
            except ValueError:
                logging.error(f"Unknown directory for {track.file}. "
                              f"You have to specify the directory on either the global level, "
                              f"group level or track list level.")
                raise ValueError
            file_path = os.path.join(root_directory, track.file)
            if not os.path.isfile(file_path):
                logging.error(f"File {file_path} does not exist")
                raise ValueError
            return file_path

    def _get_track_list_root_directory(self, group: MusicGroup, track_list: TrackList) -> str:
        """
        Returns the root directory of the track list.

        Lookup order:
        1. the directory specified directly on the track list
        2. the directory specified on the group
        3. the global directory specified

        If none of the above exists, raise a ValueError.
        """
        root_directory = track_list.directory if track_list.directory is not None else group.directory
        root_directory = root_directory if root_directory is not None else self.directory
        if root_directory is None:
            raise ValueError("Missing directory")
        return root_directory

    async def _wait_for_current_player_to_be_playing(self):
        """
        Waits until the `current_player` is playing.
        """
        if self._current_player is not None:
            while not self._current_player.is_playing():
                await asyncio.sleep(self.SLEEP_TIME)

    async def set_volume(self, volume, set_global=True, smooth=True, n_steps=20, seconds=2):
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
            logging.debug(f"Changed music volume to {volume}")
