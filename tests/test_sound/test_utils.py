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


class TestSoundTupleGenerator:
    def test_sound_tuple_generator(self):
        """
        Test that calling `sound_tuple_generator()` returns an iterator over all tuples of the form
        (group, sound, sound_file).
        """
        group_config = {
            "name": "Group 1",
            "sounds": [
                {"name": "Sound 1", "files": ["sound_file_1.wav"]},
                {"name": "Sound 2", "files": ["sound_file_2.wav", "sound_file_3.wav"]},
            ],
        }
        groups = [SoundGroup(group_config)]
        generator = utils.sound_tuple_generator(groups)
        first_tuple = (groups[0], groups[0].sounds[0], groups[0].sounds[0].files[0])
        second_tuple = (groups[0], groups[0].sounds[1], groups[0].sounds[1].files[0])
        third_tuple = (groups[0], groups[0].sounds[1], groups[0].sounds[1].files[1])
        assert first_tuple == next(generator)
        assert second_tuple == next(generator)
        assert third_tuple == next(generator)
        with pytest.raises(StopIteration):
            next(generator)
