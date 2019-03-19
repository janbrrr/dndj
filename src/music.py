import asyncio
import time
import logging
import random
import os
from collections import namedtuple
from typing import Union, Dict


class Track:

    def __init__(self, config: Union[str, Dict]):
        """
        Initializes a `Track` instance.

        If the `config` parameter is a `str`, it is expected to be the file name.
        Else it is expected to be a dictionary with the following keys:
        - "file": the filename (only the filename, excluding the directory)
        - "start_at": time at which the track should start in the %H:%M:%S format (Optional)

        :param config: `str` or `dict`
        """
        if isinstance(config, str):
            self.file = config
            start_at = None
        else:
            self.file = config["file"]
            start_at = None if "start_at" not in config else config["start_at"]
        if not self.file.endswith(".mp3"):
            raise TypeError("Music files must use the `.mp3` format.")
        if start_at is not None:
            time_struct = time.strptime(start_at, "%H:%M:%S")
            self.start_at = time_struct.tm_sec + time_struct.tm_min * 60 + time_struct.tm_hour * 60 * 60  # in sec
        else:
            self.start_at = None


class TrackList:

    def __init__(self, config: Dict):
        """
        Initializes a `TrackList` instance.

        The `dict` parameter is expected to be a dictionary with the following keys:
        - "name": the name of the track list
        - "directory": the directory where the files for this track list are (Optional)
        - "loop": bool indicating whether to loop once all tracks have been played
        - "shuffle": bool indicating whether to shuffle the tracks
        - "tracks": a list of track configs. See `Track` class for more information.

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        self.loop = config["loop"]
        self.shuffle = config["shuffle"]
        tracks = [Track(track_config) for track_config in config["tracks"]]
        self.tracks = tuple(tracks)  # immutable


class MusicGroup:

    def __init__(self, config: Dict):
        """
        Initializes a `MusicGroup` instance.

        A ``MusicGroup`` groups multiple `TrackList` instances.
        For more information have a look at the `TrackList` class.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "name": a descriptive name for the music group
        - "directory": the directory where the files for this group are (Optional)
        - "track_lists": a list of configs for `TrackList` instances. See `TrackList` class for more information

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        track_lists = [TrackList(track_list_config) for track_list_config in config["track_lists"]]
        self.track_lists = tuple(track_lists)


CurrentlyPlaying = namedtuple("CurrentlyPlaying", ["track_list", "task"])


class MusicManager:

    SLEEP_TIME = 0.01

    def __init__(self, config: Dict, music_mixer):
        """
        Initializes a `MusicManager` instance.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "volume": a value between 0 (mute) and 1 (max)
        - "groups": a list of configs for `MusicGroup` instances. See `MusicGroup` class for more information

        :param config: `dict`
        :param music_mixer: reference to `pygame.mixer.music` after it has been initialized
        """
        self.music_mixer = music_mixer
        self.volume = float(config["volume"])
        groups = [MusicGroup(group_config) for group_config in config["groups"]]
        self.groups = tuple(groups)
        self.currently_playing = None

    async def cancel(self):
        """
        If a track is currently being played, the replay will be cancelled.
        """
        if self.currently_playing is not None:
            self.currently_playing.task.cancel()
            while self.currently_playing is not None:  # wait till track list finishes cancelling
                await asyncio.sleep(self.SLEEP_TIME)

    async def play_track_list(self, group_index, track_list_index):
        """
        Creates an asynchronous task to play the track list at the given index.
        If a track list is already being played, it will be cancelled and the new track list will be played.
        """
        group = self.groups[group_index]
        track_list = group.track_lists[track_list_index]
        logging.debug(f"Received request to play music from group {group_index} at index {track_list_index} ({track_list.name})")
        await self.cancel()
        loop = asyncio.get_event_loop()
        self.currently_playing = CurrentlyPlaying(track_list,
                                                  loop.create_task(self._play_track_list(group, track_list_index)))
        logging.debug(f"Created a task to play '{track_list.name}'")
        await asyncio.sleep(self.SLEEP_TIME)  # Return to the event loop that will start the task

    async def _play_track_list(self, group: MusicGroup, track_list_index: int):
        """
        Plays the track list at the given index from the given group.
        """
        track_list = group.track_lists[track_list_index]
        try:
            logging.info(f"Loading '{track_list.name}'")
            while True:
                tracks = list(track_list.tracks)  # Copy since random will shuffle in place
                if track_list.shuffle:
                    random.shuffle(tracks)
                for track in tracks:
                    directory = track_list.directory if track_list.directory is not None else group.directory
                    self.music_mixer.load(os.path.join(directory, track.file))
                    self.music_mixer.set_volume(0)
                    self.music_mixer.play()
                    if track.start_at is not None:
                        self.music_mixer.set_pos(track.start_at)
                    logging.info(f"Now Playing: {track.file}")
                    await self.set_volume(self.volume, set_global=False)
                    while self.music_mixer.get_busy():
                        try:
                            await asyncio.sleep(self.SLEEP_TIME)
                        except asyncio.CancelledError:
                            await self.set_volume(0, set_global=False)
                            raise
                    logging.info(f"Finished playing: {track.file}")
                if not track_list.loop:
                    break
        except asyncio.CancelledError:
            self.music_mixer.stop()
            self.currently_playing = None
            logging.info(f"Cancelled '{track_list.name}'")
            raise

    async def set_volume(self, volume, set_global=True, smooth=True, n_steps=20, seconds=2):
        """
        Sets the volume for the music.

        :param volume: new volume, a value between 0 (mute) and 1 (max)
        :param set_global: whether to set this as the new global volume
        :param smooth: whether to do a smooth transitions
        :param n_steps: how many steps the transitions incorporates
        :param seconds: the time in which the transitions takes place
        """
        if not smooth:
            self.music_mixer.set_volume(volume)
        else:
            current_volume = self.music_mixer.get_volume()
            step_size = (current_volume - volume) / n_steps
            for i in range(n_steps):
                self.music_mixer.set_volume(current_volume - (i + 1) * step_size)
                await asyncio.sleep(seconds / n_steps)
        if set_global:
            self.volume = volume
            logging.debug(f"Changed music volume to {volume}")
