from typing import NamedTuple, List, Union, Dict


class Sound(NamedTuple):
    name: str
    files: List[str]

    @classmethod
    def from_dict(cls, data_dict: Union[str, Dict, List]):
        if isinstance(data_dict, list):
            return [Sound.from_dict(element) for element in data_dict]
        name = data_dict["name"]
        files = data_dict["files"]
        if isinstance(files, str):
            files = [files]
        return Sound(name=name, files=files)
