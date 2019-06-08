import collections
import logging
from typing import Iterable

import requests

import src.music.utils as utils
from src import cache
from src.music.music_group import MusicGroup


logger = logging.getLogger(__name__)


class MusicChecker:

    VALID_YOUTUBE_TRACKS_CACHE = "valid_youtube_tracks.json"

    def do_all_checks(self, groups: Iterable[MusicGroup], default_dir):
        """
        Perform all the available checks.

        :param groups: `MusicGroup` instances to check
        :param default_dir: default directory where the tracks are located
        """
        self.check_track_list_names(groups)
        self.check_tracks_do_exist(groups, default_dir)

    def check_track_list_names(self, groups: Iterable[MusicGroup]):
        """
        Iterates through every track list, checks that the names are unique and that their `next` attributes (if set)
        point to existing track list names.

        Raises a `RuntimeError` if the names are not unique or a `next` attribute points to a non-existing track list.
        """
        logger.info("Checking that track lists have unique names and their `next` parameters...")
        names = set()
        next_names = set()
        for group in groups:
            for track_list in group.track_lists:
                if track_list.name not in names:
                    names.add(track_list.name)
                else:
                    logger.error(f"Found multiple track lists with the same name '{track_list.name}'.")
                    raise RuntimeError(
                        f"The names of the track lists must be unique. Found duplicate with name "
                        f"'{track_list.name}'."
                    )
                if track_list.next is not None:
                    next_names.add(track_list.next)
        if not next_names.issubset(names):
            for next_name in next_names:
                if next_name not in names:
                    logger.error(f"'{next_name}' points to a non-existing track list.")
                    raise RuntimeError(f"'{next_name}' points to a non-existing track list.")
        logger.info("Success! Names are unique and `next` parameters point to existing track lists.")

    def check_tracks_do_exist(self, groups: Iterable[MusicGroup], default_dir):
        """
        Iterates through every track and attempts to get its path. Logs any error and re-raises any exception.
        """
        logger.info("Checking that tracks point to valid paths...")
        valid_youtube_tracks = collections.deque(cache.load(self.VALID_YOUTUBE_TRACKS_CACHE), maxlen=100)
        for group, track_list, track in utils.music_tuple_generator(groups):
            try:
                if not track.is_youtube_link:
                    utils.get_track_path(group, track_list, track, default_dir=default_dir)
                else:  # This is much faster to check if the link is a YouTube video
                    if track.file in valid_youtube_tracks:
                        continue
                    url = f"https://www.youtube.com/oembed?url={track.file}"
                    result = requests.get(url)
                    if result.status_code != 200:
                        raise RuntimeError(f"The url '{track.file}' is not a valid YouTube video.")
                    valid_youtube_tracks.append(track.file)
            except Exception as ex:
                logger.error(f"Track '{track.file}' does not point to a valid path.")
                raise ex
        cache.save(list(valid_youtube_tracks), self.VALID_YOUTUBE_TRACKS_CACHE)
        logger.info("Success! All tracks point to valid paths.")
