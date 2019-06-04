import random
from typing import Dict, List

from src.music.track import Track


class TrackList:
    def __init__(self, config: Dict):
        """
        Initializes a `TrackList` instance.

        The `dict` parameter is expected to be a dictionary with the following keys:
        - "name": the name of the track list
        - "directory": the directory where the files for this track list are (Optional)
        - "loop": bool indicating whether to loop once all tracks have been played (Optional, default=True)
        - "shuffle": bool indicating whether to shuffle the tracks (Optional, default=True)
        - "next": name of the track list to play after this one finishes (Optional)
        - "tracks": a list of track configs. See `Track` class for more information.

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        self.loop = config["loop"] if "loop" in config else True
        self.shuffle = config["shuffle"] if "shuffle" in config else True
        self.next = config["next"] if "next" in config else None
        tracks = [Track(track_config) for track_config in config["tracks"]]
        self._tracks = tuple(tracks)  # immutable

    @property
    def tracks(self) -> List[Track]:
        """
        Returns the tracks for this instance. This list is shuffled, if `shuffle` is set.
        """
        tracks = list(self._tracks)  # Copy since random will shuffle in place
        if self.shuffle:
            random.shuffle(tracks)
        return tracks

    def __eq__(self, other):
        if isinstance(other, TrackList):
            attrs_are_the_same = (
                self.name == other.name
                and self.directory == other.directory
                and self.loop == other.loop
                and self.shuffle == other.shuffle
            )
            if not attrs_are_the_same:
                return False
            if len(self._tracks) != len(other._tracks):
                return False
            for my_track, other_track in zip(self._tracks, other._tracks):
                if my_track != other_track:
                    return False
            return True
        return False
