import logging
import os
from functools import lru_cache
from typing import Generator, Iterable, Tuple

import pafy

from src.music.music_group import MusicGroup
from src.music.track import Track
from src.music.track_list import TrackList


logger = logging.getLogger(__name__)


def music_tuple_generator(groups: Iterable[MusicGroup]) -> Generator[Tuple[MusicGroup, TrackList, Track], None, None]:
    """
    Iterates through the groups, the tracklists in the groups and returns a tuple
    (group, track_list, track) for every track.
    """
    for group in groups:
        for track_list in group.track_lists:
            for track in track_list.tracks:
                yield (group, track_list, track)


@lru_cache(maxsize=50)
def get_audio_stream(youtube_url: str):
    """
    Returns the url to the audio stream of the given url corresponding to a YouTube video.
    """
    youtube_video = pafy.new(youtube_url)
    best_audio_stream = youtube_video.getbestaudio()
    return best_audio_stream.url


def get_track_list_root_directory(group: MusicGroup, track_list: TrackList, default_dir=None) -> str:
    """
    Returns the root directory of the track list.

    Lookup order:
    1. the directory specified directly on the track list
    2. the directory specified on the group
    3. the default directory if specified

    If none of the above exists, raise a ValueError.
    """
    root_directory = track_list.directory if track_list.directory is not None else group.directory
    root_directory = root_directory if root_directory is not None else default_dir
    if root_directory is None:
        raise ValueError(f"Missing directory for group={group.name} and track_list={track_list.name}.")
    return root_directory


def get_track_path(group: MusicGroup, track_list: TrackList, track: Track, default_dir=None) -> str:
    """
    Returns the path of the `Track` instance that should be played.

    If the `file` attribute is a link to a YouTube video, get the corresponding
    URL for the audio stream and return it.

    Otherwise assume that the `file` attribute refers to a file location. Return the file path.
    Raises a `ValueError` if the file path is not valid.

    :param group: `MusicGroup` where the `track_list` is in
    :param track_list: `TrackList` where the `track` is in
    :param track: the `Track` instance that should be played
    :param default_dir: the default directory to use if no other is specified
    :return: path to the `track` location that the VLC player can understand
    """
    if track.is_youtube_link:
        return get_audio_stream(track.file)
    try:
        root_directory = get_track_list_root_directory(group, track_list, default_dir=default_dir)
    except ValueError as error:
        logger.error(
            f"Unknown directory for {track.file}. "
            f"You have to specify the directory on either the default level, "
            f"group level or track list level."
        )
        raise error
    file_path = os.path.join(root_directory, track.file)
    if not os.path.isfile(file_path):
        logger.error(f"File {file_path} does not exist")
        raise ValueError(f"The path {file_path} does not point to an existing file.")
    return file_path
