from unittest.mock import MagicMock, call

import pytest

from src.music import MusicGroup
from src.music.music_checker import MusicChecker


class TestMusicChecker:
    def test_do_all_checks(self, monkeypatch):
        """
        Test that the `do_all_checks()` method does all the checks.
        """
        check_track_list_names_mock = MagicMock()
        check_tracks_do_exist_mock = MagicMock()
        monkeypatch.setattr(MusicChecker, "check_track_list_names", check_track_list_names_mock)
        monkeypatch.setattr(MusicChecker, "check_tracks_do_exist", check_tracks_do_exist_mock)
        groups = []
        MusicChecker().do_all_checks(groups, "default/dir/")
        check_track_list_names_mock.assert_called_once_with(groups)
        check_tracks_do_exist_mock.assert_called_once_with(groups, "default/dir/")

    def test_check_track_list_names_raises_error_if_duplicate_name(self):
        """
        If two tracklists have the same name, raise a `RuntimeError`.
        """
        group_config = {
            "name": "Group 1",
            "track_lists": [{"name": "Track List", "tracks": []}, {"name": "Track List", "tracks": []}],
        }
        groups = [MusicGroup(group_config)]
        with pytest.raises(RuntimeError):
            MusicChecker().check_track_list_names(groups)

    def test_check_track_list_names_raises_error_if_next_invalid_name(self):
        """
        If the `next` attribute of a tracklist is not the name of an existing tracklist, raise a `RuntimeError`.
        """
        group_config = {
            "name": "Group 1",
            "track_lists": [{"name": "Track List", "next": "Non-existing Track List", "tracks": []}],
        }
        groups = [MusicGroup(group_config)]
        with pytest.raises(RuntimeError):
            MusicChecker().check_track_list_names(groups)

    def test_check_track_list_names(self):
        """
        If all names are unique and the `next` attributes are names of existing tracklists, no error should be raised.
        """
        group_config = {
            "name": "Group 1",
            "track_lists": [{"name": "First", "next": "Second", "tracks": []}, {"name": "Second", "tracks": []}],
        }
        groups = [MusicGroup(group_config)]
        MusicChecker().check_track_list_names(groups)
        assert True  # No error occurred

    def test_check_tracks_do_exist(self, monkeypatch):
        """
        Test that the `check_tracks_do_exist()` method uses `utils.get_track_path()` to determine whether a file exists.
        """
        get_track_path_mock = MagicMock()
        monkeypatch.setattr("src.music.music_checker.utils.get_track_path", get_track_path_mock)
        group_1 = MusicGroup(
            {"name": "Group 1", "track_lists": [{"name": "Track List 1", "tracks": ["track-1.mp3", "track-2.mp3"]}]}
        )
        group_2 = MusicGroup({"name": "Group 2", "track_lists": [{"name": "Track List 2", "tracks": ["track-3.mp3"]}]})
        expected_calls = [
            call(group_1, group_1.track_lists[0], group_1.track_lists[0]._tracks[0], default_dir="default/dir/"),
            call(group_1, group_1.track_lists[0], group_1.track_lists[0]._tracks[1], default_dir="default/dir/"),
            call(group_2, group_2.track_lists[0], group_2.track_lists[0]._tracks[0], default_dir="default/dir/"),
        ]
        MusicChecker().check_tracks_do_exist([group_1, group_2], "default/dir/")
        assert get_track_path_mock.call_count == 3  # There are three tracks in total to check
        get_track_path_mock.assert_has_calls(expected_calls, any_order=True)

    def test_check_tracks_do_exist_does_not_raise_on_valid_youtube_video(self):
        """
        Test that the `check_tracks_do_exist()` method does not raise an error on existing YouTube videos.
        """
        group = MusicGroup(
            {
                "name": "Group 1",
                "track_lists": [
                    {
                        "name": "Track List 1",
                        "tracks": ["https://www.youtube.com/watch?v=hKRUPYrAQoE"],  # Some existing video
                    }
                ],
            }
        )
        MusicChecker().check_tracks_do_exist([group], None)
        assert True  # Success if no error was raised

    def test_check_tracks_do_exist_raises_on_private_youtube_video(self):
        """
        Test that the `check_tracks_do_exist()` method raises an error for private YouTube videos.
        """
        group = MusicGroup(
            {
                "name": "Group 1",
                "track_lists": [
                    {
                        "name": "Track List 1",
                        "tracks": ["https://www.youtube.com/watch?v=lTutay89N6Q"],  # Some private video
                    }
                ],
            }
        )
        with pytest.raises(RuntimeError):
            MusicChecker().check_tracks_do_exist([group], None)

    def test_check_tracks_do_exist_raises_on_invalid_youtube_video(self):
        """
        Test that the `check_tracks_do_exist()` method raises an error for non-existing YouTube videos.
        """
        group = MusicGroup(
            {
                "name": "Group 1",
                "track_lists": [
                    {
                        "name": "Track List 1",
                        "tracks": ["https://www.youtube.com/watch?v=l1111111111"],  # Some non-existent video
                    }
                ],
            }
        )
        with pytest.raises(RuntimeError):
            MusicChecker().check_tracks_do_exist([group], None)

    def test_check_tracks_do_exist_raises_error_if_file_does_not_exist(self):
        """
        Test that `check_tracks_do_exist()´ re-raises the `ValueError` raised by `get_track_path()` if the track
        is not a valid file.
        """
        group = MusicGroup(
            {"name": "Group 1", "track_lists": [{"name": "Track List 1", "tracks": ["this-does-not-exist.mp3"]}]}
        )
        with pytest.raises(ValueError):
            MusicChecker().check_tracks_do_exist([group], None)
