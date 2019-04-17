from typing import Dict

from src.music.track_list import TrackList


class MusicGroup:

    def __init__(self, config: Dict):
        """
        Initializes a `MusicGroup` instance.

        A ``MusicGroup`` groups multiple `TrackList` instances.
        For more information have a look at the `TrackList` class.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "name": a descriptive name for the music group
        - "directory": the directory where the files for this group are (Optional)
        - "sort": whether to sort the track lists alphabetically (Optional, default=True)
        - "track_lists": a list of configs for `TrackList` instances. See `TrackList` class for more information

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        track_lists = [TrackList(track_list_config) for track_list_config in config["track_lists"]]
        if "sort" not in config or ("sort" in config and config["sort"]):
            track_lists = sorted(track_lists, key=lambda x: x.name)
        self.track_lists = tuple(track_lists)

    def __eq__(self, other):
        if isinstance(other, MusicGroup):
            attrs_are_the_same = self.name == other.name and self.directory == other.directory
            if not attrs_are_the_same:
                return False
            if len(self.track_lists) != len(other.track_lists):
                return False
            for my_track_list, other_track_list in zip(self.track_lists, other.track_lists):
                if my_track_list != other_track_list:
                    return False
            return True
        return False
