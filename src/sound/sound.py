from typing import Dict

from src.sound.sound_file import SoundFile


class Sound:

    def __init__(self, config: Dict):
        """
        Initializes a `Sound` instance.

        A ``Sound`` is not necessarily a single sound file. It is possible to specify a list of sound files. In this
        case a file will be chosen at random when the sound is being played.

        For example, you can associate four different sword sound files with a single sound named 'Sword Swing'.
        When playing this sound, a random sword sound of the provided list will be played.

        The `config` parameter is expected to be a dictionary with the following keys:
        - "name": a descriptive name for the sound
        - "directory": the directory where the files for this sound are (Optional)
        - "files": a list of files (or `SoundFile` configs) associated with this sound

        :param config: `dict`
        """
        self.name = config["name"]
        self.directory = config["directory"] if "directory" in config else None
        files = [SoundFile(sound_file) for sound_file in config["files"]]
        self.files = tuple(files)

    def __eq__(self, other):
        if isinstance(other, Sound):
            attrs_are_the_same = self.name == other.name and self.directory == other.directory
            if not attrs_are_the_same:
                return False
            if len(self.files) != len(other.files):
                return False
            for my_file, other_file in zip(self.files, other.files):
                if my_file != other_file:
                    return False
            return True
        return False
