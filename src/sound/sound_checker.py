import logging
import os
from typing import Iterable

import pygame.mixer
from pydub.utils import mediainfo

from src.sound import SoundGroup, utils


logger = logging.getLogger(__name__)


class SoundChecker:
    def __init__(self, groups: Iterable[SoundGroup], default_dir):
        """
        Initializes a `SoundChecker` instance.

        :param groups: `SoundGroup` instances to check
        :param default_dir: default directory where the sounds are located
        """
        self.groups = groups
        self.default_dir = default_dir

    def do_all_checks(self):
        """
        Perform all the available checks.
        """
        self.check_sound_files_do_exist()
        self.check_sound_files_can_be_played()

    def check_sound_files_do_exist(self):
        """
        Iterates through every sound file and attempts to get its path. Logs any error and raises a `ValueError`
        if a file path is invalid.
        """
        logger.info("Checking that sounds point to valid paths...")
        for group in self.groups:
            for sound in group.sounds:
                try:
                    root_directory = utils.get_sound_root_directory(group, sound, default_dir=self.default_dir)
                except ValueError as ex:
                    logger.error(f"Sound '{sound.name}' is missing the directory.")
                    raise ex
                for sound_file in sound.files:
                    file_path = os.path.join(root_directory, sound_file.file)
                    if not os.path.isfile(file_path):
                        logger.error(f"File {file_path} does not exist")
                        raise ValueError(f"File {file_path} does not exist")
        logger.info("Success! All sounds point to valid paths.")

    def check_sound_files_can_be_played(self):
        """
        Iterates through every sound file and attempts to create a player that uses this file. Logs any error and
        raises a `TypeError` if a file has an unsupported format.
        """
        logger.info("Checking that sounds are playable...")
        for group, sound, sound_file in utils.sound_tuple_generator(self.groups):
            root_directory = utils.get_sound_root_directory(group, sound, default_dir=self.default_dir)
            sound_file_path = os.path.join(root_directory, sound_file.file)
            try:
                pygame.mixer.Sound(sound_file_path)
            except pygame.error:
                logger.error(f"File {sound_file_path} cannot be played. Its format is unsupported.")
                file_info = mediainfo(sound_file_path)
                logger.error(
                    f"Found format: codec={file_info['codec_long_name']}, "
                    f"sample_rate={file_info['sample_rate']}, channels={file_info['channels']}"
                )
                logger.error("Note that only signed 16-bit sample formats are supported.")
                logger.error("You can convert your file with the script in 'scripts/convert_file.py'.")
                raise TypeError(f"File {sound_file_path} cannot be played. Its format is unsupported.")
        logger.info("Success! All sounds can be played.")
