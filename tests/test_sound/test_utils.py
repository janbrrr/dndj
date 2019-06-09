import pytest

import src.sound.utils as utils
from src.sound import SoundGroup


class TestGetSoundRootDirectory:
    @pytest.fixture
    def example_group(self):
        group_config = {"name": "Group 1", "sounds": [{"name": "Sound 1", "files": ["sound_1.wav"]}]}
        return SoundGroup(group_config)

    def test_get_sound_root_directory_returns_global_directory(self, example_group):
        """
        If a directory is specified at the default level and no other level, return the default directory.
        """
        example_group.directory = None
        sound = example_group.sounds[0]
        sound.directory = None
        directory = utils.get_sound_root_directory(group=example_group, sound=sound, default_dir="default/dir")
        assert directory == "default/dir"

    def test_get_sound_root_directory_returns_group_directory(self, example_group):
        """
        When a directory is specified for a SoundGroup and no directory is specified for the Sound, the
        group directory should be returned (not the default directory).
        """
        example_group.directory = "group/dir"
        sound = example_group.sounds[0]
        sound.directory = None
        directory = utils.get_sound_root_directory(group=example_group, sound=sound, default_dir="default/dir")
        assert directory == "group/dir"

    def test_get_sound_root_directory_returns_sound_directory(self, example_group):
        """
        When a directory is specified for a Sound, it should be returned (not the default or group directory).
        """
        example_group.directory = "group/dir"
        sound = example_group.sounds[0]
        sound.directory = "sound/dir"
        directory = utils.get_sound_root_directory(group=example_group, sound=sound, default_dir="default/dir")
        assert directory == "sound/dir"

    def test_get_sound_root_directory_raises_value_error_if_no_directory_on_any_level(self, example_group):
        """
        If no directory is specified at all (neither the default, group or sound level), then raise a ValueError.
        """
        example_group.directory = None
        sound = example_group.sounds[0]
        sound.directory = None
        with pytest.raises(ValueError):
            utils.get_sound_root_directory(group=example_group, sound=sound, default_dir=None)
