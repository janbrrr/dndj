import os
import pytest
from unittest.mock import MagicMock
from asynctest import CoroutineMock

from src.sound import SoundGroup, SoundManager


class TestSoundManager:

    @pytest.fixture
    def minimal_sound_manager_config(self):
        return {
            "volume": 1,
            "groups": []
        }

    @pytest.fixture
    def example_sound_manager(self, example_config):
        return SoundManager(config=example_config["sound"])

    def test_minimal_dict_as_config(self, minimal_sound_manager_config):
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert sound_manager.volume == 1
        assert len(sound_manager.groups) == 0

    def test_groups_are_created(self, minimal_sound_manager_config):
        sound_group_1_config = {
            "name": "Some Sound Group 1",
            "sounds": []
        }
        sound_group_2_config = {
            "name": "Some Sound Group 2",
            "sounds": []
        }
        minimal_sound_manager_config["groups"] = [
            sound_group_1_config,
            sound_group_2_config
        ]
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert len(sound_manager.groups) == 2
        assert sound_manager.groups[0] == SoundGroup(sound_group_1_config)
        assert sound_manager.groups[1] == SoundGroup(sound_group_2_config)

    def test_directory_is_none_by_default(self, minimal_sound_manager_config):
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert sound_manager.directory is None

    def test_directory_in_config(self, minimal_sound_manager_config):
        minimal_sound_manager_config["directory"] = "/some/dir/"
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert sound_manager.directory == "/some/dir/"

    def test_groups_are_sorted_by_name_by_default(self, minimal_sound_manager_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "sounds": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "sounds": []
        }
        minimal_sound_manager_config["groups"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert sound_manager.groups[0] == SoundGroup(name_starts_with_a_config)
        assert sound_manager.groups[1] == SoundGroup(name_starts_with_n_config)

    def test_sort_in_config(self, minimal_sound_manager_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "sounds": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "sounds": []
        }
        minimal_sound_manager_config["sort"] = False
        minimal_sound_manager_config["groups"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert sound_manager.groups[0] == SoundGroup(name_starts_with_n_config)
        assert sound_manager.groups[1] == SoundGroup(name_starts_with_a_config)

    def test_sound_groups_use_tuple_instead_of_list(self, minimal_sound_manager_config):
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert isinstance(sound_manager.groups, tuple)

    async def test_play_sound_uses_correct_file_path(self, example_sound_manager, monkeypatch):
        """
        Test that the `_play_sound()` method instantiates the `pygame.mixer.Sound` with the file path of the sound file
        """
        sound_class_mock = MagicMock()
        monkeypatch.setattr("src.sound.sound_manager.pygame.mixer.Sound", sound_class_mock)
        monkeypatch.setattr("src.sound.sound_manager.asyncio.sleep", CoroutineMock())
        group = example_sound_manager.groups[0]
        sound = group.sounds[0]
        assert len(sound.files) == 1  # make sure it is only one since they are chosen at random
        sound_file = sound.files[0]
        await example_sound_manager._play_sound(group, sound)
        sound_class_mock.assert_called_once_with(
            os.path.join(example_sound_manager._get_sound_root_directory(group, sound), sound_file.file)
        )

    async def test_play_sound_sets_volume_and_plays(self, example_sound_manager, monkeypatch):
        """
        Test that the `_play_sound()` method sets the volume on the `pygame.mixer.Sound` instance with the
        configured volume, that it starts to play the sound and waits for it to finish.

        This test assumes no `end_at` attribute on the sound, so make sure to remove it.
        """
        sound_instance_mock = MagicMock()
        sound_instance_mock.get_length.return_value = 42
        sleep_mock = CoroutineMock()
        monkeypatch.setattr("src.sound.sound_manager.pygame.mixer.Sound", MagicMock(return_value=sound_instance_mock))
        monkeypatch.setattr("src.sound.sound_manager.asyncio.sleep", sleep_mock)
        group = example_sound_manager.groups[0]
        sound = group.sounds[0]
        assert len(sound.files) == 1  # make sure it is only one since they are chosen at random
        sound_file = sound.files[0]
        sound_file.end_at = None  # Test without end_at
        await example_sound_manager._play_sound(group, sound)
        sound_instance_mock.set_volume.assert_called_once_with(example_sound_manager.volume)
        sound_instance_mock.play.assert_called_once_with()
        sound_instance_mock.get_length.assert_called_once()
        sleep_mock.assert_called_once_with(42)  # same as sound_instance.get_length()

    async def test_play_sound_sets_volume_and_plays_with_end_at(self, example_sound_manager, monkeypatch):
        """
        Test that the `_play_sound()` method sets the volume on the `pygame.mixer.Sound` instance with the
        configured volume, that it starts to play the sound and waits for it to finish.

        This test assumes the `end_at` attribute on the sound to be set, so make sure to set it.
        Make sure the `play()` method is called appropriately and the method should sleep for the correct
         amount of time.
        """
        sound_instance_mock = MagicMock()
        sleep_mock = CoroutineMock()
        monkeypatch.setattr("src.sound.sound_manager.pygame.mixer.Sound", MagicMock(return_value=sound_instance_mock))
        monkeypatch.setattr("src.sound.sound_manager.asyncio.sleep", sleep_mock)
        group = example_sound_manager.groups[0]
        sound = group.sounds[0]
        assert len(sound.files) == 1  # make sure it is only one since they are chosen at random
        sound_file = sound.files[0]
        sound_file.end_at = 4000
        await example_sound_manager._play_sound(group, sound)
        sound_instance_mock.set_volume.assert_called_once_with(example_sound_manager.volume)
        sound_instance_mock.play.assert_called_once_with(maxtime=sound_file.end_at)
        sleep_mock.assert_called_once_with(sound_file.end_at / 1000)  # in seconds

    def test_get_sound_root_directory_returns_global_directory(self, example_sound_manager):
        """
        If a directory is specified at the global level and no other level, return the global directory.
        """
        example_sound_manager.directory = "global/dir"
        first_group = example_sound_manager.groups[0]
        first_group.directory = None
        first_sound_in_first_group = first_group.sounds[0]
        first_sound_in_first_group.directory = None
        directory = example_sound_manager._get_sound_root_directory(group=first_group, sound=first_sound_in_first_group)
        assert directory == "global/dir"

    def test_get_sound_root_directory_returns_group_directory(self, example_sound_manager):
        """
        When a directory is specified for a SoundGroup and no directory is specified for the Sound, the
        group directory should be returned (not the global directory).
        """
        example_sound_manager.directory = "global/dir"
        first_group = example_sound_manager.groups[0]
        first_group.directory = "group/dir"
        first_sound_in_first_group = first_group.sounds[0]
        first_sound_in_first_group.directory = None
        directory = example_sound_manager._get_sound_root_directory(group=first_group, sound=first_sound_in_first_group)
        assert directory == "group/dir"

    def test_get_sound_root_directory_returns_sound_directory(self, example_sound_manager):
        """
        When a directory is specified for a Sound, it should be returned (not the global or group directory).
        """
        example_sound_manager.directory = "global/dir"
        first_group = example_sound_manager.groups[0]
        first_group.directory = "group/dir"
        first_sound_in_first_group = first_group.sounds[0]
        first_sound_in_first_group.directory = "sound/dir"
        directory = example_sound_manager._get_sound_root_directory(group=first_group, sound=first_sound_in_first_group)
        assert directory == "sound/dir"

    def test_get_sound_root_directory_raises_value_error_if_no_directory_on_any_level(self, example_sound_manager):
        """
        If no directory is specified at all (neither the global, group or sound level), then raise a ValueError.
        """
        example_sound_manager.directory = None
        first_group = example_sound_manager.groups[0]
        first_group.directory = None
        first_sound_in_first_group = first_group.sounds[0]
        first_sound_in_first_group.directory = None
        with pytest.raises(ValueError):
            example_sound_manager._get_sound_root_directory(group=first_group, sound=first_sound_in_first_group)

    def test_set_volume(self, example_sound_manager):
        example_sound_manager.volume = 1
        example_sound_manager.set_volume(0)
        assert example_sound_manager.volume == 0
