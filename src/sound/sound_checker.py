import logging
import os
from typing import Iterable

from src.sound import SoundGroup, utils


logger = logging.getLogger(__name__)


class SoundChecker:
    def do_all_checks(self, groups: Iterable[SoundGroup], default_dir):
        """
        Perform all the available checks.

        :param groups: `SoundGroup` instances to check
        :param default_dir: default directory where the sounds are located
        """
        self.check_sound_files_do_exist(groups, default_dir)

    def check_sound_files_do_exist(self, groups: Iterable[SoundGroup], default_dir):
        """
        Iterates through every sound file and attempts to get its path. Logs any error and raises a `ValueError`
        if a file path is invalid.
        """
        logger.info("Checking that sounds point to valid paths...")
        for group in groups:
            for sound in group.sounds:
                try:
                    root_directory = utils.get_sound_root_directory(group, sound, default_dir=default_dir)
                except ValueError as ex:
                    logger.error(f"Sound '{sound.name}' is missing the directory.")
                    raise ex
                for sound_file in sound.files:
                    file_path = os.path.join(root_directory, sound_file.file)
                    if not os.path.isfile(file_path):
                        logger.error(f"File {file_path} does not exist")
                        raise ValueError
        logger.info("Success! All sounds point to valid paths.")
