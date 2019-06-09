from src.sound.sound import Sound
from src.sound.sound_group import SoundGroup


def get_sound_root_directory(group: SoundGroup, sound: Sound, default_dir=None) -> str:
    """
    Returns the root directory of the sound.

    Lookup order:
    1. the directory specified directly on the sound
    2. the directory specified on the group
    3. the default directory specified

    If none of the above exists, raise a ValueError.
    """
    root_directory = sound.directory if sound.directory is not None else group.directory
    root_directory = root_directory if root_directory is not None else default_dir
    if root_directory is None:
        raise ValueError(f"Sound '{sound.name}' is missing directory.")
    return root_directory
