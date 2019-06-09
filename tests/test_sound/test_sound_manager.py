import asyncio
import os
from unittest.mock import MagicMock, call

import pytest
from asynctest import CoroutineMock

from src.sound import SoundGroup, SoundManager, utils


class TestSoundManager:
    @pytest.fixture
    def minimal_sound_manager_config(self):
        return {"volume": 1, "groups": []}

    @pytest.fixture
    def example_sound_manager(self, example_config, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr("src.sound.sound_manager.SoundChecker", MagicMock())
            manager = SoundManager(config=example_config["sound"])
        return manager

    def test_minimal_dict_as_config(self, minimal_sound_manager_config):
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert sound_manager.volume == 1
        assert len(sound_manager.groups) == 0

    def test_groups_are_created(self, minimal_sound_manager_config):
        sound_group_1_config = {"name": "Some Sound Group 1", "sounds": []}
        sound_group_2_config = {"name": "Some Sound Group 2", "sounds": []}
        minimal_sound_manager_config["groups"] = [sound_group_1_config, sound_group_2_config]
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
        name_starts_with_n_config = {"name": "Not First In The Alphabet", "sounds": []}
        name_starts_with_a_config = {"name": "Alphabet", "sounds": []}
        minimal_sound_manager_config["groups"] = [name_starts_with_n_config, name_starts_with_a_config]
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert sound_manager.groups[0] == SoundGroup(name_starts_with_a_config)
        assert sound_manager.groups[1] == SoundGroup(name_starts_with_n_config)

    def test_sort_in_config(self, minimal_sound_manager_config):
        name_starts_with_n_config = {"name": "Not First In The Alphabet", "sounds": []}
        name_starts_with_a_config = {"name": "Alphabet", "sounds": []}
        minimal_sound_manager_config["sort"] = False
        minimal_sound_manager_config["groups"] = [name_starts_with_n_config, name_starts_with_a_config]
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert sound_manager.groups[0] == SoundGroup(name_starts_with_n_config)
        assert sound_manager.groups[1] == SoundGroup(name_starts_with_a_config)

    def test_sound_groups_use_tuple_instead_of_list(self, minimal_sound_manager_config):
        sound_manager = SoundManager(minimal_sound_manager_config)
        assert isinstance(sound_manager.groups, tuple)

    def test_equal_if_same_config(self):
        manager_1 = SoundManager({"volume": 1, "groups": []})
        manager_2 = SoundManager({"volume": 1, "groups": []})
        assert manager_1 == manager_2
        assert manager_2 == manager_1

    def test_not_equal_if_different_attributes(self):
        manager_1 = SoundManager({"volume": 1, "groups": []})
        manager_2 = SoundManager({"volume": 0.5, "groups": []})
        assert manager_1 != manager_2
        assert manager_2 != manager_1

    def test_not_equal_if_different_number_of_groups(self):
        manager_1 = SoundManager({"volume": 1, "groups": []})
        manager_2 = SoundManager({"volume": 1, "groups": [{"name": "Group", "sounds": []}]})
        assert manager_1 != manager_2
        assert manager_2 != manager_1

    def test_not_equal_if_different_groups(self):
        manager_1 = SoundManager({"volume": 1, "groups": [{"name": "Unique Group", "sounds": []}]})
        manager_2 = SoundManager({"volume": 1, "groups": [{"name": "Normal Group", "sounds": []}]})
        assert manager_1 != manager_2
        assert manager_2 != manager_1

    def test_not_equal_if_different_types(self):
        config = {"volume": 1, "groups": [{"name": "Group", "sounds": []}]}
        manager = SoundManager(config)
        assert config != manager
        assert manager != config

    def test_performs_checks_on_initialization(self, monkeypatch):
        do_all_checks_mock = MagicMock()
        monkeypatch.setattr("src.sound.sound_manager.SoundChecker.do_all_checks", do_all_checks_mock)
        manager = SoundManager({"volume": 1, "directory": "default/dir/", "groups": []})
        do_all_checks_mock.assert_called_once_with(manager.groups, manager.directory)

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
        await example_sound_manager._play_sound(MagicMock(), 0, 0)
        sound_class_mock.assert_called_once_with(
            os.path.join(
                utils.get_sound_root_directory(group, sound, default_dir=example_sound_manager.directory),
                sound_file.file,
            )
        )

    async def test_play_sound_file_sets_volume_and_plays(self, example_sound_manager, monkeypatch):
        """
        Test that the `_play_sound_file()` method sets the volume on the `pygame.mixer.Sound` instance with the
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
        await example_sound_manager._play_sound_file("root", sound_file)
        sound_instance_mock.set_volume.assert_called_once_with(example_sound_manager.volume)
        sound_instance_mock.play.assert_called_once_with()
        sound_instance_mock.get_length.assert_called_once()
        sleep_mock.assert_called_once_with(42)  # same as sound_instance.get_length()

    async def test_play_sound_file_sets_volume_and_plays_with_end_at(self, example_sound_manager, monkeypatch):
        """
        Test that the `_play_sound_file()` method sets the volume on the `pygame.mixer.Sound` instance with the
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
        await example_sound_manager._play_sound_file("root", sound_file)
        sound_instance_mock.set_volume.assert_called_once_with(example_sound_manager.volume)
        sound_instance_mock.play.assert_called_once_with(maxtime=sound_file.end_at)
        sleep_mock.assert_called_once_with(sound_file.end_at / 1000)  # in seconds

    async def test_play_sound_file_stops_if_cancelled(self, example_sound_manager, monkeypatch):
        """
        Test that the `_play_sound_file()` method will call `stop()` on the `pygame.mixer.Sound` instance if cancelled.
        """
        sound_instance_mock = MagicMock()
        monkeypatch.setattr("src.sound.sound_manager.pygame.mixer.Sound", MagicMock(return_value=sound_instance_mock))
        # Waiting for the sound to end (aka. sleeping) will cause a CancelledError via a side effect
        monkeypatch.setattr("src.sound.sound_manager.asyncio.sleep", CoroutineMock(side_effect=asyncio.CancelledError))
        group = example_sound_manager.groups[0]
        sound = group.sounds[0]
        assert len(sound.files) == 1  # make sure it is only one since they are chosen at random
        sound_file = sound.files[0]
        sound_file.end_at = None  # Test without end_at
        with pytest.raises(asyncio.CancelledError):
            await example_sound_manager._play_sound_file("root", sound_file)
        expected_calls = [
            call.set_volume(example_sound_manager.volume),
            call.play(),
            call.get_length(),  # to sleep for this length
            call.stop(),
        ]
        assert sound_instance_mock.mock_calls == expected_calls

    def test_set_volume(self, example_sound_manager):
        example_sound_manager.volume = 1
        example_sound_manager.set_volume(0)
        assert example_sound_manager.volume == 0

    async def test_currently_playing(self, example_sound_manager, loop):
        """
        Test that the `currently_playing` property correctly returns the active sounds as tracked by the `SoundTracker`.
        """
        assert len(example_sound_manager.currently_playing) == 0
        dummy_task_one = loop.create_task(asyncio.sleep(0.001))
        dummy_task_two = loop.create_task(asyncio.sleep(0.001))
        example_sound_manager.tracker.register_sound(0, 0, dummy_task_one)
        example_sound_manager.tracker.register_sound(0, 1, dummy_task_two)
        currently_playing = example_sound_manager.currently_playing
        assert len(currently_playing) == 2
        assert currently_playing[0].group_index == 0
        assert currently_playing[0].group_name == example_sound_manager.groups[0].name
        assert currently_playing[0].sound_index == 0
        assert currently_playing[0].sound_name == example_sound_manager.groups[0].sounds[0].name
        assert currently_playing[1].group_index == 0
        assert currently_playing[1].group_name == example_sound_manager.groups[0].name
        assert currently_playing[1].sound_index == 1
        assert currently_playing[1].sound_name == example_sound_manager.groups[0].sounds[1].name
