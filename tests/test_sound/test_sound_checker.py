import os
from unittest.mock import MagicMock, call

import pytest

from src.sound import SoundGroup
from src.sound.sound_checker import SoundChecker


class TestSoundChecker:
    def test_do_all_checks(self, monkeypatch):
        """
        Test that the `do_all_checks()` method does all the checks.
        """
        check_sound_files_do_exist_mock = MagicMock()
        monkeypatch.setattr(SoundChecker, "check_sound_files_do_exist", check_sound_files_do_exist_mock)
        groups = []
        SoundChecker().do_all_checks(groups, "default/dir/")
        check_sound_files_do_exist_mock.assert_called_once_with(groups, "default/dir/")

    def test_check_sound_files_do_exist(self, monkeypatch):
        """
        Test that `check_sound_files_do_exist()` checks whether the sound files exist at their respective locations.
        """
        get_sound_root_directory_mock = MagicMock(return_value="root")
        is_file_mock = MagicMock()
        monkeypatch.setattr("src.sound.sound_checker.utils.get_sound_root_directory", get_sound_root_directory_mock)
        monkeypatch.setattr("src.sound.sound_checker.os.path.isfile", is_file_mock)

        group_1 = SoundGroup(
            {"name": "Group 1", "sounds": [{"name": "Sound 1", "files": ["sound-1.wav", "sound-2.wav"]}]}
        )
        group_2 = SoundGroup({"name": "Group 2", "sounds": [{"name": "Sound 2", "files": ["sound-3.wav"]}]})
        SoundChecker().check_sound_files_do_exist([group_1, group_2], "default/dir")
        expected_get_root_calls = [
            call(group_1, group_1.sounds[0], default_dir="default/dir"),
            call(group_2, group_2.sounds[0], default_dir="default/dir"),
        ]
        assert get_sound_root_directory_mock.call_count == 2  # There are two sounds in total
        get_sound_root_directory_mock.assert_has_calls(expected_get_root_calls, any_order=True)
        expected_is_file_calls = [
            call(os.path.join("root", group_1.sounds[0].files[0].file)),
            call(os.path.join("root", group_1.sounds[0].files[1].file)),
            call(os.path.join("root", group_2.sounds[0].files[0].file)),
        ]
        assert is_file_mock.call_count == 3  # There are three sound files in total to check
        is_file_mock.assert_has_calls(expected_is_file_calls, any_order=True)

    def test_check_sound_files_do_exist_re_raises_exception(self):
        """
        Test that `check_sound_files_do_exist()´ re-raises the `ValueError` raised by `utils.get_sound_root_directory()`
        if the sound has no root directory.
        """
        group = SoundGroup({"name": "Group 1", "sounds": [{"name": "Sound 1", "files": ["no-directory.wav"]}]})
        with pytest.raises(ValueError):
            SoundChecker().check_sound_files_do_exist([group], None)

    def test_check_sound_files_do_exist_raises_exception_if_file_invalid(self):
        """
        Test that `check_sound_files_do_exist()´ raises a `ValueError` if the file path of a sound is invalid.
        """
        group = SoundGroup({"name": "Group 1", "sounds": [{"name": "Sound 1", "files": ["file-does-not-exist.wav"]}]})
        with pytest.raises(ValueError):
            SoundChecker().check_sound_files_do_exist([group], "dir")
