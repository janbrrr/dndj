from unittest.mock import MagicMock

import pytest

import src.music.utils as utils
from src.music import MusicGroup


class TestMusicTupleGenerator:
    def test_music_tuple_generator(self):
        """
        Test that calling `music_tuple_generator()` returns an iterator over all tuples of the form
        (group, track_list, track).
        """
        group_config = {
            "name": "Group 1",
            "track_lists": [
                {"name": "Track List 1", "shuffle": False, "tracks": ["track_1.mp3"]},
                {"name": "Track List 2", "shuffle": False, "tracks": ["track_2.mp3", "track_3.mp3"]},
            ],
        }
        groups = [MusicGroup(group_config)]
        generator = utils.music_tuple_generator(groups)
        first_tuple = (groups[0], groups[0].track_lists[0], groups[0].track_lists[0].tracks[0])
        second_tuple = (groups[0], groups[0].track_lists[1], groups[0].track_lists[1].tracks[0])
        third_tuple = (groups[0], groups[0].track_lists[1], groups[0].track_lists[1].tracks[1])
        assert first_tuple == next(generator)
        assert second_tuple == next(generator)
        assert third_tuple == next(generator)
        with pytest.raises(StopIteration):
            next(generator)


class TestGetAudioStream:
    def test_get_audio_stream_uses_pafy(self, monkeypatch):
        """
        This test ensures that `get_audio_stream()` uses `pafy` to obtain the best audio stream.
        """
        pafy_mock = MagicMock()
        youtube_video_mock = MagicMock()
        audio_stream_mock = MagicMock()
        audio_stream_mock.url = "some-url"
        pafy_mock.new.return_value = youtube_video_mock
        youtube_video_mock.getbestaudio.return_value = audio_stream_mock
        monkeypatch.setattr("src.music.utils.pafy", pafy_mock)

        youtube_url = "https://www.youtube.com/watch?v=jIxas0a-KgM"
        best_audio_stream = utils.get_audio_stream(youtube_url)
        assert best_audio_stream == "some-url"

    def test_get_audio_stream_does_not_raise(self):
        """
        This test ensures that `pafy` and `youtube-dl` do not raise any exceptions when getting the
        url of the audio stream.
        """
        youtube_url = "https://www.youtube.com/watch?v=jIxas0a-KgM"
        _ = utils.get_audio_stream(youtube_url)
        assert True  # No error


class TestGetTrackListRootDirectory:
    @pytest.fixture
    def example_group(self):
        group_config = {"name": "Group 1", "track_lists": [{"name": "Track List", "tracks": []}]}
        return MusicGroup(group_config)

    def test_get_track_list_root_directory_returns_default_directory(self, example_group):
        """
        If a directory is specified at the default level and no other level, return the default directory.
        """
        example_group.directory = None
        example_track_list = example_group.track_lists[0]
        example_track_list.directory = None
        directory = utils.get_track_list_root_directory(
            group=example_group, track_list=example_track_list, default_dir="global/dir"
        )
        assert directory == "global/dir"

    def test_get_track_list_root_directory_returns_group_directory(self, example_group):
        """
        If a directory is specified at the MusicGroup level and not the TrackList level, return the MusicGroup directory
        (even if there is a default directory specified).
        """
        example_group.directory = "group/dir"
        example_track_list = example_group.track_lists[0]
        example_track_list.directory = None
        directory = utils.get_track_list_root_directory(
            group=example_group, track_list=example_track_list, default_dir="global/dir"
        )
        assert directory == "group/dir"

    def test_get_track_list_root_directory_returns_track_list_directory(self, example_group):
        """
        If a directory is specified at the TrackList, return it (even if there is a default directory and a
        MusicGroup directory specified).
        """
        example_group.directory = "group/dir"
        example_track_list = example_group.track_lists[0]
        example_track_list.directory = "track/list/dir"
        directory = utils.get_track_list_root_directory(
            group=example_group, track_list=example_track_list, default_dir="global/dir"
        )
        assert directory == "track/list/dir"

    def test_get_track_list_root_directory_raises_value_error_if_no_directory_on_any_level(self, example_group):
        """
        If no directory is specified at all (neither the default, MusicGroup or TrackList level),
        then raise a ValueError.
        """
        example_group.directory = None
        example_track_list = example_group.track_lists[0]
        example_track_list.directory = None
        with pytest.raises(ValueError):
            utils.get_track_list_root_directory(group=example_group, track_list=example_track_list)


class TestGetTrackPath:
    @pytest.fixture
    def example_group(self):
        group_config = {"name": "Group 1", "track_lists": [{"name": "Track List", "tracks": ["track_1.mp3"]}]}
        return MusicGroup(group_config)

    def test_get_track_path_returns_audio_url_if_track_is_youtube_link(self, example_group, monkeypatch):
        """
        If the `file` attribute of a `Track` is the link to a YouTube video, return the url of its audio stream.
        """
        track_list = example_group.track_lists[0]
        track = track_list.tracks[0]
        track.file = "https://www.youtube.com/watch?v=jIxas0a-KgM"
        get_audio_stream_mock = MagicMock(return_value="some-url")
        monkeypatch.setattr("src.music.utils.get_audio_stream", get_audio_stream_mock)
        path = utils.get_track_path(example_group, track_list, track)
        assert path == "some-url"

    def test_get_track_path_returns_file_path_if_track_is_file(self, example_group, monkeypatch):
        """
        If the `file` attribute of a `Track` is not the link to a YouTube video, return the file path.
        """
        monkeypatch.setattr("src.music.utils.get_track_list_root_directory", MagicMock(return_value="root/dir/"))
        monkeypatch.setattr("src.music.utils.os.path.isfile", lambda x: True)
        track_list = example_group.track_lists[0]
        track = track_list.tracks[0]
        track.file = "file.mp3"
        path = utils.get_track_path(example_group, track_list, track)
        assert path == "root/dir/file.mp3"

    def test_get_track_path_raises_value_error_if_root_directory_unknown(self, example_group):
        """
        If the `file` attribute of a `Track` is not the link to a YouTube video, return the file path. The file path
        consists of the root directory combined with the filename. If there is no root directory, raise a `ValueError`.
        """
        example_group.directory = None
        track_list = example_group.track_lists[0]
        track_list.directory = None
        track = track_list.tracks[0]
        track.file = "file.mp3"
        with pytest.raises(ValueError):
            utils.get_track_path(example_group, track_list, track)

    def test_get_track_path_raises_value_error_if_path_is_not_existing_file(self, example_group, monkeypatch):
        """
        If the `file` attribute of a `Track` is not the link to a YouTube video, return the file path. But if the file
        path does not refer to an existing file, raise a `ValueError`.
        """
        track_list = example_group.track_lists[0]
        track = track_list.tracks[0]
        track.file = "file.mp3"
        monkeypatch.setattr(
            "src.music.utils.get_track_list_root_directory", MagicMock(return_value="root/dir/")
        )  # non-existing dir
        with pytest.raises(ValueError):
            utils.get_track_path(example_group, track_list, track)
