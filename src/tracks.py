import time
from typing import NamedTuple, List, Union, Dict


class Track(NamedTuple):
    file_path: str
    start_at: Union[None, int] = None  # in ms

    @classmethod
    def from_dict(cls, data_dict: Union[str, Dict, List]):
        if isinstance(data_dict, list):
            return [Track.from_dict(element) for element in data_dict]
        if isinstance(data_dict, str):  # only a file_path
            return Track(file_path=data_dict)
        file_path = data_dict["file_path"]
        start_at = None if "start_at" not in data_dict else data_dict["start_at"]
        if start_at is not None:
            time_struct = (time.strptime(start_at, "%H:%M:%S"))
            start_at = time_struct.tm_sec * 1000 + time_struct.tm_min * 1000 * 60 + time_struct.tm_hour * 1000 * 60 * 60
        return Track(file_path=file_path, start_at=start_at)


class TrackList(NamedTuple):
    name: str
    loop: bool
    shuffle: bool
    tracks: List[Track]

    @classmethod
    def from_dict(cls, data_dict: Union[Dict, List]):
        if isinstance(data_dict, list):
            return [TrackList.from_dict(element) for element in data_dict]
        return TrackList(name=data_dict["name"], loop=data_dict["loop"], shuffle=data_dict["shuffle"],
                         tracks=Track.from_dict(data_dict["tracks"]))
