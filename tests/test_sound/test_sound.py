from unittest.mock import MagicMock

import pytest

from src.sound import Sound, SoundFile


class TestSound:
    @pytest.fixture
    def minimal_sound_config(self):
        return {"name": "Some Name", "files": []}

    def test_minimal_dict_as_config(self, minimal_sound_config):
        sound = Sound(minimal_sound_config)
        assert sound.name == "Some Name"
        assert len(sound.files) == 0

    def test_sounds_are_created(self, minimal_sound_config):
        minimal_sound_config["files"] = ["some-filename.wav", "other-filename.wav"]
        sound = Sound(minimal_sound_config)
        assert len(sound.files) == 2
        assert sound.files[0] == SoundFile("some-filename.wav")
        assert sound.files[1] == SoundFile("other-filename.wav")

    def test_directory_is_none_by_default(self, minimal_sound_config):
        sound = Sound(minimal_sound_config)
        assert sound.directory is None

    def test_directory_in_config(self, minimal_sound_config):
        minimal_sound_config["directory"] = "/some/dir/"
        sound = Sound(minimal_sound_config)
        assert sound.directory == "/some/dir/"

    def test_loop_is_false_by_default(self, minimal_sound_config):
        sound = Sound(minimal_sound_config)
        assert sound.loop is False

    def test_loop_delay_is_zero_by_default(self, minimal_sound_config):
        sound = Sound(minimal_sound_config)
        assert sound.loop_delay == 0

    def test_loop_delay_single_int(self):
        sound = Sound({"name": "Sound", "files": [], "loop_delay": 42})
        assert sound._loop_delay_min == 42
        assert sound._loop_delay_max == 42
        assert sound.loop_delay == 42
        sound.loop_delay = 24
        assert sound._loop_delay_min == 24
        assert sound._loop_delay_max == 24

    def test_loop_delay_interval(self):
        sound = Sound({"name": "Sound", "files": [], "loop_delay": "24-42"})
        assert sound._loop_delay_min == 24
        assert sound._loop_delay_max == 42
        loop_delay_sample_value = sound.loop_delay
        assert loop_delay_sample_value >= 24
        assert loop_delay_sample_value <= 42
        sound.loop_delay = "25-43"
        assert sound._loop_delay_min == 25
        assert sound._loop_delay_max == 43

    def test_raises_value_error_if_loop_delay_neither_int_nor_string_type(self):
        with pytest.raises(ValueError):
            Sound({"name": "Sound", "files": [], "loop_delay": 5.6})
        sound = Sound({"name": "Sound", "files": [], "loop_delay": "42"})
        with pytest.raises(ValueError):
            sound.loop_delay = 12.5

    def test_raises_value_error_if_loop_delay_neither_int_nor_interval(self):
        with pytest.raises(ValueError):
            Sound({"name": "Sound", "files": [], "loop_delay": "?"})
        sound = Sound({"name": "Sound", "files": [], "loop_delay": "42"})
        with pytest.raises(ValueError):
            sound.loop_delay = "?"

    def test_raises_value_error_if_loop_delay_interval_max_higher_than_min(self):
        with pytest.raises(ValueError):
            Sound({"name": "Sound", "files": [], "loop_delay": "42-24"})
        sound = Sound({"name": "Sound", "files": [], "loop_delay": "42"})
        with pytest.raises(ValueError):
            sound.loop_delay = "42-24"

    def test_loop_delay_interval_returns_random_value_in_range(self, monkeypatch):
        randint_mock = MagicMock(return_value=42)
        monkeypatch.setattr("src.sound.sound.random.randint", randint_mock)
        sound = Sound({"name": "Sound", "files": [], "loop_delay": "24-42"})
        assert sound.loop_delay == 42
        randint_mock.assert_called_once_with(sound._loop_delay_min, sound._loop_delay_max)

    def test_files_use_tuple_instead_of_list(self, minimal_sound_config):
        sound = Sound(minimal_sound_config)
        assert isinstance(sound.files, tuple)

    def test_equal_if_same_config(self):
        sound_1 = Sound({"name": "Sound", "files": []})
        sound_2 = Sound({"name": "Sound", "files": []})
        assert sound_1 == sound_2
        assert sound_2 == sound_1

    def test_not_equal_if_different_attributes(self):
        sound_1 = Sound({"name": "Sound 1", "files": []})
        sound_2 = Sound({"name": "Sound 2", "files": []})
        assert sound_1 != sound_2
        assert sound_2 != sound_1

    def test_not_equal_if_different_number_of_files(self):
        sound_1 = Sound({"name": "Sound", "files": []})
        sound_2 = Sound({"name": "Sound", "files": ["some-filename.wav"]})
        assert sound_1 != sound_2
        assert sound_2 != sound_1

    def test_not_equal_if_different_files(self):
        sound_1 = Sound({"name": "Sound", "files": ["unique-filename.wav"]})
        sound_2 = Sound({"name": "Sound", "files": ["some-filename.wav"]})
        assert sound_1 != sound_2
        assert sound_2 != sound_1

    def test_not_equal_if_different_types(self):
        config = {"name": "Sound", "files": []}
        sound = Sound(config)
        assert sound != config
        assert config != sound
