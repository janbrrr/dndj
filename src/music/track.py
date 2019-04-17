import time

from typing import Union, Dict


class Track:

    def __init__(self, config: Union[str, Dict]):
        """
        Initializes a `Track` instance.

        If the `config` parameter is a `str`, it is expected to be the filename.
        Else it is expected to be a dictionary with the following keys:
        - "file": the filename (only the filename, excluding the directory) (can be a link to a YouTube video)
        - "start_at": time at which the track should start in the %H:%M:%S format (Optional)
        - "end_at": time at which the track should end in the %H:%M:%S format (Optional)

        :param config: `str` or `dict`
        """
        if isinstance(config, str):
            self.file = config
            start_at = None
            end_at = None
        else:
            self.file = config["file"]
            start_at = None if "start_at" not in config else config["start_at"]
            end_at = None if "end_at" not in config else config["end_at"]
        self.start_at = self._convert_formatted_time_to_ms(start_at) if start_at is not None else None
        self.end_at = self._convert_formatted_time_to_ms(end_at) if end_at is not None else None

    def _convert_formatted_time_to_ms(self, formatted_time: str) -> int:
        """
        Converts a string in the format %H:%M:%S to the corresponding number of milliseconds.

        :param formatted_time: string in the format %H:%M:%S
        """
        time_struct = time.strptime(formatted_time, "%H:%M:%S")
        return (time_struct.tm_sec + time_struct.tm_min * 60 + time_struct.tm_hour * 3600) * 1000

    def __eq__(self, other):
        if isinstance(other, Track):
            return self.file == other.file and self.start_at == other.start_at and self.end_at == other.end_at
        return False
