import asyncio
import time
import logging
import random
import os
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
        - "loop": bool indicating whether to loop once all tracks have been played
        - "shuffle": bool indicating whether to shuffle the tracks
        - "tracks": a list of track configs. See `Track` class for more information.

        :param config: `dict`
        """
        self.name = config["name"]
        self.loop = config["loop"]
        self.shuffle = config["shuffle"]
        tracks = [Track(track_config) for track_config in config["tracks"]]
        self.tracks = tuple(tracks)  # immutable


class MusicManager:

    SLEEP_TIME = 0.01

    def __init__(self, config_dict: Dict, music_mixer):
        """
        Initializes a `MusicManager` instance.

        The `dict` parameter is expected to be a dictionary with the following keys:
        - "volume": a value between 0 (mute) and 1 (max)
        - "directory": the directory where the files are
        - "track_lists": a list of track_list configs. See `TrackList` class for more information

        :param config_dict: `dict`
        :param music_mixer: reference to `pygame.mixer.music` after it has been initialized
        """
        self.music_mixer = music_mixer
        self.volume = float(config_dict["volume"])
        self.directory = config_dict["directory"]
        track_lists = [TrackList(track_list_config) for track_list_config in config_dict["track_lists"]]
        self.track_lists = tuple(track_lists)
        self.currently_playing = None

    def cancel(self):
        """
        If a track is currently being played, the replay will be cancelled.
        """
        if self.currently_playing is not None:
            self.currently_playing.cancel()
            self.currently_playing = None

    async def play_track_list(self, index):
        """
        Creates an asynchronous task to play the track list at the given index.
        If a track list is already being played, it will be cancelled and the new track list will be played.
        """
        track_list = self.track_lists[index]
        self.cancel()
        loop = asyncio.get_event_loop()
        self.currently_playing = loop.create_task(self._play_track_list(track_list))
        await asyncio.sleep(self.SLEEP_TIME)  # Return to the event loop that will start the task

    async def _play_track_list(self, track_list: TrackList):
        """
        Plays the given track list.
        """
        logging.debug(f"Loading '{track_list.name}'")
        while True:
            tracks = list(track_list.tracks)  # Copy since random will shuffle in place
            if track_list.shuffle:
                random.shuffle(tracks)
            for track in tracks:
                self.music_mixer.load(os.path.join(self.directory, track.file))
                self.music_mixer.set_volume(self.volume)
                self.music_mixer.play()
                if track.start_at is not None:
                    self.music_mixer.set_pos(track.start_at)
                logging.info(f"Now Playing: {track.file}")
                while self.music_mixer.get_busy():
                    try:
                        await asyncio.sleep(self.SLEEP_TIME)
                    except asyncio.CancelledError:
                        self.music_mixer.stop()
                        logging.info(f"Stopped {track.file}")
                        raise
                logging.info(f"Finished playing: {track.file}")
            if not track_list.loop:
                break

    def set_volume(self, volume, smooth=True, n_steps=10, seconds=0.5):
        """
        Sets the volume for the music.

        :param volume: new volume, a value between 0 (mute) and 1 (max)
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
                time.sleep(seconds / n_steps)
        self.volume = volume
        logging.debug(f"Changed music volume to {volume}")
