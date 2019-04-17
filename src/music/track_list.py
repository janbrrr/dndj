from typing import Dict

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
        - "tracks": a list of track configs. See `Track` class for more information.

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        self.loop = config["loop"] if "loop" in config else True
        self.shuffle = config["shuffle"] if "shuffle" in config else True
        tracks = [Track(track_config) for track_config in config["tracks"]]
        self.tracks = tuple(tracks)  # immutable

    def __eq__(self, other):
        if isinstance(other, TrackList):
            attrs_are_the_same = self.name == other.name and self.directory == other.directory \
                                 and self.loop == other.loop and self.shuffle == other.shuffle
            if not attrs_are_the_same:
                return False
            if len(self.tracks) != len(other.tracks):
                return False
            for my_track, other_track in zip(self.tracks, other.tracks):
                if my_track != other_track:
                    return False
            return True
        return False
