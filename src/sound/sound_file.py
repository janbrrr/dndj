import time
from typing import Dict, Union


class SoundFile:

    def __init__(self, config: Union[str, Dict]):
        """
        Initializes a `SoundFile` instance.

        The `config` parameter is either a `str` containing the filename or a dictionary with the following keys:
        - "file": the filename
        - "end_at": time at which the sound should end in the %H:%M:%S format (Optional)

        :param config: String containing the filename or a dictionary containing the config
        """
        if isinstance(config, str):
            self.file = config
            self.end_at = None
        else:
            self.file = config["file"]
            end_at = config["end_at"] if "end_at" in config else None
            if end_at is not None:
                time_struct = time.strptime(end_at, "%H:%M:%S")
                self.end_at = (time_struct.tm_sec + time_struct.tm_min * 60 + time_struct.tm_hour * 60 * 60) \
                              * 1000  # in ms
            else:
                self.end_at = None
        if not self.file.endswith(".wav") and not self.file.endswith(".ogg"):
            raise TypeError("Sound files must use the `.wav` or `.ogg` format.")

    def __eq__(self, other):
        if isinstance(other, SoundFile):
            return self.file == other.file and self.end_at == other.end_at
        return False
