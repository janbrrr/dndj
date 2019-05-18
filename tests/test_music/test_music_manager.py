import asyncio
from unittest.mock import MagicMock, call, PropertyMock

import pytest
from asynctest import CoroutineMock

from src.music import MusicGroup, MusicManager, Track
from src.music.music_manager import CurrentlyPlaying


class TestMusicManager:

    @pytest.fixture
    def minimal_music_manager_config(self):
        return {
            "volume": 50,
            "groups": []
        }

    @pytest.fixture
    def example_music_manager(self, example_config, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr("src.music.music_manager.MusicManager._check_tracks_are_valid", MagicMock())
            manager = MusicManager(config=example_config["music"])
        return manager

    def test_minimal_dict_as_config(self, minimal_music_manager_config):
        music_manager = MusicManager(minimal_music_manager_config)
        assert music_manager.volume == 50
        assert len(music_manager.groups) == 0

    def test_groups_are_created(self, minimal_music_manager_config):
        music_group_1_config = {
            "name": "Some Music Group 1",
            "track_lists": []
        }
        music_group_2_config = {
            "name": "Some Music Group 2",
            "track_lists": []
        }
        minimal_music_manager_config["groups"] = [
            music_group_1_config,
            music_group_2_config
        ]
        music_manager = MusicManager(minimal_music_manager_config)
        assert len(music_manager.groups) == 2
        assert music_manager.groups[0] == MusicGroup(music_group_1_config)
        assert music_manager.groups[1] == MusicGroup(music_group_2_config)

    def test_directory_is_none_by_default(self, minimal_music_manager_config):
        music_manager = MusicManager(minimal_music_manager_config)
        assert music_manager.directory is None

    def test_directory_in_config(self, minimal_music_manager_config):
        minimal_music_manager_config["directory"] = "/some/dir/"
        music_manager = MusicManager(minimal_music_manager_config)
        assert music_manager.directory == "/some/dir/"

    def test_groups_are_sorted_by_name_by_default(self, minimal_music_manager_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "track_lists": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "track_lists": []
        }
        minimal_music_manager_config["groups"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        music_manager = MusicManager(minimal_music_manager_config)
        assert music_manager.groups[0] == MusicGroup(name_starts_with_a_config)
        assert music_manager.groups[1] == MusicGroup(name_starts_with_n_config)

    def test_sort_in_config(self, minimal_music_manager_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "track_lists": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "track_lists": []
        }
        minimal_music_manager_config["sort"] = False
        minimal_music_manager_config["groups"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        music_manager = MusicManager(minimal_music_manager_config)
        assert music_manager.groups[0] == MusicGroup(name_starts_with_n_config)
        assert music_manager.groups[1] == MusicGroup(name_starts_with_a_config)

    def test_music_groups_use_tuple_instead_of_list(self, minimal_music_manager_config):
        music_manager = MusicManager(minimal_music_manager_config)
        assert isinstance(music_manager.groups, tuple)

    def test_equal_if_same_config(self):
        manager_1 = MusicManager({
            "volume": 1,
            "groups": []
        })
        manager_2 = MusicManager({
            "volume": 1,
            "groups": []
        })
        assert manager_1 == manager_2
        assert manager_2 == manager_1

    def test_not_equal_if_different_attributes(self):
        manager_1 = MusicManager({
            "volume": 1,
            "groups": []
        })
        manager_2 = MusicManager({
            "volume": 0.5,
            "groups": []
        })
        assert manager_1 != manager_2
        assert manager_2 != manager_1

    def test_not_equal_if_different_number_of_groups(self):
        manager_1 = MusicManager({
            "volume": 1,
            "groups": []
        })
        manager_2 = MusicManager({
            "volume": 1,
            "groups": [{
                "name": "Group",
                "track_lists": []
            }]
        })
        assert manager_1 != manager_2
        assert manager_2 != manager_1

    def test_not_equal_if_different_groups(self):
        manager_1 = MusicManager({
            "volume": 1,
            "groups": [{
                "name": "Some Group",
                "track_lists": []
            }]
        })
        manager_2 = MusicManager({
            "volume": 1,
            "groups": [{
                "name": "Different Group",
                "track_lists": []
            }]
        })
        assert manager_1 != manager_2
        assert manager_2 != manager_1

    def test_not_equal_if_different_types(self):
        config = {
            "volume": 1,
            "groups": [{
                "name": "Some Group",
                "track_lists": []
            }]
        }
        manager = MusicManager(config)
        assert config != manager
        assert manager != config

    def test_check_tracks_are_valid_is_called_on_initialization(self, monkeypatch):
        check_tracks_are_valid_mock = MagicMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager._check_tracks_are_valid", check_tracks_are_valid_mock)
        _ = MusicManager({
            "volume": 1,
            "groups": []
        })
        check_tracks_are_valid_mock.assert_called_once()

    def test_check_tracks_are_valid(self, monkeypatch):
        get_track_path_mock = MagicMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_path", get_track_path_mock)
        manager = MusicManager({
            "volume": 1,
            "groups": [
                {
                    "name": "Group 1",
                    "track_lists": [
                        {
                            "name": "Track List 1",
                            "tracks": [
                                "track-1.mp3",
                                "track-2.mp3"
                            ]
                        }
                    ]
                },
                {
                    "name": "Group 2",
                    "track_lists": [
                        {
                            "name": "Track List 2",
                            "tracks": [
                                "track-3.mp3"
                            ]
                        }
                    ]
                }
            ]
        })
        group_1 = manager.groups[0]
        group_2 = manager.groups[1]
        expected_calls = [
            call(group_1, group_1.track_lists[0], group_1.track_lists[0]._tracks[0]),
            call(group_1, group_1.track_lists[0], group_1.track_lists[0]._tracks[1]),
            call(group_2, group_2.track_lists[0], group_2.track_lists[0]._tracks[0]),
        ]
        assert get_track_path_mock.call_count == 3  # There are three tracks in total to check
        get_track_path_mock.assert_has_calls(expected_calls, any_order=True)

    def test_check_tracks_are_valid_does_not_raise_on_valid_youtube_video(self, monkeypatch):
        config = {
            "volume": 1,
            "groups": [
                {
                    "name": "Group 1",
                    "track_lists": [
                        {
                            "name": "Track List 1",
                            "tracks": [
                                "https://www.youtube.com/watch?v=hKRUPYrAQoE"  # Some existing video
                            ]
                        }
                    ]
                }
            ]
        }
        _ = MusicManager(config)
        assert True  # Success if no error was raised

    def test_check_tracks_are_valid_raises_on_private_youtube_video(self, monkeypatch):
        config = {
            "volume": 1,
            "groups": [
                {
                    "name": "Group 1",
                    "track_lists": [
                        {
                            "name": "Track List 1",
                            "tracks": [
                                "https://www.youtube.com/watch?v=lTutay89N6Q"  # Some private video
                            ]
                        }
                    ]
                }
            ]
        }
        with pytest.raises(RuntimeError):
            _ = MusicManager(config)

    def test_check_tracks_are_valid_raises_on_invalid_youtube_video(self, monkeypatch):
        config = {
            "volume": 1,
            "groups": [
                {
                    "name": "Group 1",
                    "track_lists": [
                        {
                            "name": "Track List 1",
                            "tracks": [
                                "https://www.youtube.com/watch?v=l1111111111"  # Some non-existent video
                            ]
                        }
                    ]
                }
            ]
        }
        with pytest.raises(RuntimeError):
            _ = MusicManager(config)

    def test_check_tracks_are_valid_re_raises_exception(self):
        """
        Test that `_check_tracks_are_valid()´ re-raises the `ValueError` raised by `_get_track_path()` if the track
        is not a valid file.
        """
        config = {
            "volume": 1,
            "groups": [
                {
                    "name": "Group 1",
                    "track_lists": [
                        {
                            "name": "Track List 1",
                            "tracks": [
                                "file-does-not-exist.mp3"
                            ]
                        }
                    ]
                }
            ]
        }
        with pytest.raises(ValueError):
            _ = MusicManager(config)

    def test_check_track_list_names_is_called_on_initialization(self, monkeypatch):
        check_track_list_names_mock = MagicMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager._check_track_list_names", check_track_list_names_mock)
        _ = MusicManager({
            "volume": 1,
            "groups": []
        })
        check_track_list_names_mock.assert_called_once()

    def test_check_track_list_names_raises_error_if_duplicate_name(self):
        """
        If two tracklists have the same name, raise a `RuntimeError`.
        """
        config = {
            "volume": 1,
            "groups": [
                {
                    "name": "Group 1",
                    "track_lists": [
                        {
                            "name": "Track List",
                            "tracks": []
                        },
                        {
                            "name": "Track List",
                            "tracks": []
                        }
                    ]
                }
            ]
        }
        with pytest.raises(RuntimeError):
            _ = MusicManager(config)

    def test_check_track_list_names_raises_error_if_next_invalid_name(self):
        """
        If the `next` attribute of a tracklist is not the name of an existing tracklist, raise a `RuntimeError`.
        """
        config = {
            "volume": 1,
            "groups": [
                {
                    "name": "Group 1",
                    "track_lists": [
                        {
                            "name": "Track List",
                            "next": "Non-existing Track List",
                            "tracks": []
                        }
                    ]
                }
            ]
        }
        with pytest.raises(RuntimeError):
            _ = MusicManager(config)

    def test_check_track_list_names(self):
        """
        If all names are unique and the `next` attributes are names of existing tracklists, no error should be raised.
        """
        config = {
            "volume": 1,
            "groups": [
                {
                    "name": "Group 1",
                    "track_lists": [
                        {
                            "name": "First",
                            "next": "Second",
                            "tracks": []
                        },
                        {
                            "name": "Second",
                            "tracks": []
                        }
                    ]
                }
            ]
        }
        _ = MusicManager(config)
        assert True  # No error occurred

    async def test_cancel_cancels_currently_playing(self, example_music_manager, monkeypatch):
        """
        Calling cancel() will cancel whatever is currently_playing and wait for it to reset the state.
        """
        def reset(x):
            example_music_manager._currently_playing = None
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", CoroutineMock(side_effect=reset))
        currently_playing_mock = MagicMock()
        example_music_manager._currently_playing = currently_playing_mock
        await example_music_manager.cancel(request=None)
        assert example_music_manager._currently_playing is None
        currently_playing_mock.task.cancel.assert_called_once()

    async def test_play_track_list_creates_a_task_to_play_the_track_list(self, example_music_manager, monkeypatch):
        """
        Calling play_track_list() should create a task for running _play_track_list() and set the currently_playing
        attribute.
        """
        cancel_mock = CoroutineMock()
        play_track_list_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", CoroutineMock())
        monkeypatch.setattr("src.music.music_manager.MusicManager.cancel", cancel_mock)
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_track_list", play_track_list_mock)
        assert example_music_manager._currently_playing is None
        await example_music_manager.play_track_list(request=None, group_index=0, track_list_index=0)
        cancel_mock.assert_awaited()
        assert example_music_manager._currently_playing is not None
        assert isinstance(example_music_manager._currently_playing, CurrentlyPlaying)
        assert example_music_manager._currently_playing.group_index == 0
        assert example_music_manager._currently_playing.track_list_index == 0
        assert isinstance(example_music_manager._currently_playing.task, asyncio.Task)

    async def test_play_track_list_plays_all_tracks_once_if_no_loop(self, example_music_manager, monkeypatch):
        """
        The _play_track_list() method should call _play_track() for every track in it.
        """
        play_track_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_track", play_track_mock)
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track_list._tracks = [Track("track-1.mp3"), Track("track-2.mp3")]
        track_list.loop = False
        await example_music_manager._play_track_list(request=None, group_index=0, track_list_index=0)
        assert play_track_mock.await_count == 2
        play_track_mock.assert_has_awaits([call(group, track_list, track_list._tracks[0]),
                                           call(group, track_list, track_list._tracks[1])], any_order=True)

    async def test_play_track_list_loops(self, example_music_manager, monkeypatch):
        """
        The _play_track_list() method should call _play_track() for every track in it. If all tracks have been played
        and the `loop` attribute is set on the track_list, repeat.
        """
        play_track_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_track", play_track_mock)
        group = example_music_manager.groups[0]
        track_list = MagicMock()
        track_list.tracks = [Track("track-1.mp3"), Track("track-2.mp3")]
        loop_property = PropertyMock(side_effect=[True, False])
        type(track_list).loop = loop_property
        group.track_lists = [track_list]
        await example_music_manager._play_track_list(request=None, group_index=0, track_list_index=0)
        assert play_track_mock.await_count == 4  # loops once again over two tracks
        assert loop_property.call_count == 2

    async def test_play_track_list_raises_cancelled_error_if_playing_a_track_is_cancelled(self, example_music_manager,
                                                                                          monkeypatch):
        """
        The _play_track_list() calls _play_track() for every track in it. If _play_track() raises a CancelledError,
        re-raise it.
        """
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_track",
                            CoroutineMock(side_effect=asyncio.CancelledError))
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track_list._tracks = [Track("track-1.mp3"), Track("track-2.mp3")]
        with pytest.raises(asyncio.CancelledError):
            await example_music_manager._play_track_list(request=None, group_index=0, track_list_index=0)

    async def test_play_track_list_resets_state_after_playing(self, example_music_manager, monkeypatch):
        """
        After finishing playing the tracks in the track_list, reset the state:
        - Stop the music
        - Set currently_playing to None
        - Set current_player to None
        """
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_track", CoroutineMock())
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track_list.loop = False
        track_list._tracks = [Track("track-1.mp3"), Track("track-2.mp3")]
        example_music_manager._currently_playing = True
        current_player_mock = MagicMock()
        example_music_manager._current_player = current_player_mock
        await example_music_manager._play_track_list(request=None, group_index=0, track_list_index=0)
        current_player_mock.stop.assert_called_once()
        assert example_music_manager._currently_playing is None
        assert example_music_manager._current_player is None

    async def test_play_track_list_resets_state_if_cancelled(self, example_music_manager, monkeypatch):
        """
        If the task is cancelled, reset the state.
        """
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_track",
                            CoroutineMock(side_effect=asyncio.CancelledError))
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track_list._tracks = [Track("track-1.mp3"), Track("track-2.mp3")]
        example_music_manager._currently_playing = True
        current_player_mock = MagicMock()
        example_music_manager._current_player = current_player_mock
        with pytest.raises(asyncio.CancelledError):
            await example_music_manager._play_track_list(request=None, group_index=0, track_list_index=0)
        current_player_mock.stop.assert_called_once()
        assert example_music_manager._currently_playing is None
        assert example_music_manager._current_player is None

    async def test_play_track_list_starts_next_track_list_if_finishes_playing(self, example_music_manager, monkeypatch):
        """
        If `_play_track_list()` finishes playing a track_list, `_play_next_track_list()` should be called with the
        current request and the current track_list (that finished playing).
        """
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_track", CoroutineMock())
        play_next_track_list_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_next_track_list", play_next_track_list_mock)
        track_list = example_music_manager.groups[0].track_lists[0]
        track_list.loop = False
        track_list.next = "Next Track List"
        await example_music_manager._play_track_list(request=None, group_index=0, track_list_index=0)
        play_next_track_list_mock.assert_awaited_once_with(None, track_list)

    async def test_play_track_list_does_not_start_next_track_list_if_cancelled(self, example_music_manager,
                                                                               monkeypatch):
        """
        If `_play_track_list()` is cancelled for some reason, `_play_next_track_list()` should NOT be called since
        the request has been cancelled.
        """
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_track",
                            CoroutineMock(side_effect=asyncio.CancelledError))
        play_next_track_list_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager._play_next_track_list", play_next_track_list_mock)
        track_list = example_music_manager.groups[0].track_lists[0]
        track_list.loop = False
        track_list.next = "Next Track List"
        with pytest.raises(asyncio.CancelledError):
            await example_music_manager._play_track_list(request=None, group_index=0, track_list_index=0)
        play_next_track_list_mock.assert_not_awaited()

    async def test_play_next_track_list(self, example_music_manager, monkeypatch):
        """
        The method `_play_next_track_list()` should look for the group index and track list of the track list with
        the name specified in the `next` attribute in the `current_track_list`. If the specified track list exists,
        the method `play_track_list()` should be called accordingly to start a task to play the next track list.
        """
        play_track_list_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager.play_track_list", play_track_list_mock)
        track_list = example_music_manager.groups[0].track_lists[0]
        track_list.name = "Next Track List"
        track_list.next = "Next Track List"
        await example_music_manager._play_next_track_list(None, track_list)
        play_track_list_mock.assert_awaited_once_with(None, 0, 0)

    async def test_play_next_track_list_does_nothing_if_next_is_none(self, example_music_manager, monkeypatch):
        """
        The method `_play_next_track_list()` should only look for the next track list, if the `next` attribute of
        the `current_track_list` is set.
        """
        play_track_list_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.MusicManager.play_track_list", play_track_list_mock)
        track_list = example_music_manager.groups[0].track_lists[0]
        track_list.name = "Next Track List"
        track_list.next = None
        await example_music_manager._play_next_track_list(None, track_list)
        play_track_list_mock.assert_not_awaited()

    async def test_play_track_cancels_if_get_path_raises_value_error(self, example_music_manager, monkeypatch):
        """
        The _get_track_path() method will raise a ValueError, if it fails. In that case raise a CancelledError.
        """
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_path", MagicMock(side_effect=ValueError))
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        with pytest.raises(asyncio.CancelledError):
            await example_music_manager._play_track(group=group, track_list=track_list, track=track)

    async def test_play_track_cancels_if_play_returns_error(self, example_music_manager, monkeypatch):
        """
        If calling the play() method on the media player returns an error code (-1), raise a CancelledError.
        """
        media_player_mock = MagicMock()
        media_player_mock.play.return_value = -1
        monkeypatch.setattr("src.music.music_manager.vlc.MediaPlayer", MagicMock(return_value=media_player_mock))
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_path", MagicMock(return_value="url"))
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        with pytest.raises(asyncio.CancelledError):
            await example_music_manager._play_track(group=group, track_list=track_list, track=track)

    async def test_play_track_cancels_if_cancelled_error_is_raised_while_playing(self, example_music_manager,
                                                                                 monkeypatch):
        """
        If a CancelledError is raised while the music is playing, catch it, set the volume to zero and
        re-raise it.
        """
        media_player_mock = MagicMock()
        media_player_mock.is_playing.return_value = True
        media_player_mock.get_time = MagicMock(side_effect=asyncio.CancelledError)  # some method in the try block
        set_volume_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.vlc.MediaPlayer", MagicMock(return_value=media_player_mock))
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_path", MagicMock(return_value="url"))
        monkeypatch.setattr("src.music.music_manager.MusicManager._wait_for_current_player_to_be_playing",
                            CoroutineMock())
        monkeypatch.setattr("src.music.music_manager.MusicManager.set_volume", set_volume_mock)
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", CoroutineMock())
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        track.end_at = 1000
        with pytest.raises(asyncio.CancelledError):
            await example_music_manager._play_track(group=group, track_list=track_list, track=track)
        media_player_mock.get_time.assert_called_once()  # this raised the CancelledError which got re-raised
        set_volume_mock.assert_awaited_with(0, set_global=False)

    async def test_play_track_plays_the_track(self, example_music_manager, monkeypatch):
        """
        When a track is requested to be played, perform the following steps:
        - Get the path (url or file path) for the track
        - Create a MediaPlayer instance
        - Call the play() method on the media player
        - Wait for it to start playing
        - Set the volume with set_volume()
        - While the media player is_playing(), wait
        """
        media_player_mock = MagicMock()
        is_playing_mock = MagicMock(side_effect=[True, True, False])  # Only plays for 2 steps
        media_player_mock.is_playing = is_playing_mock
        get_track_path_mock = MagicMock(return_value="url")
        sleep_mock = CoroutineMock()
        wait_for_start_mock = CoroutineMock()
        set_volume_mock = CoroutineMock()  # necessary because it will use asyncio.sleep and mess up the numbers
        monkeypatch.setattr("src.music.music_manager.vlc.MediaPlayer", MagicMock(return_value=media_player_mock))
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_path", get_track_path_mock)
        monkeypatch.setattr("src.music.music_manager.MusicManager._wait_for_current_player_to_be_playing",
                            wait_for_start_mock)
        monkeypatch.setattr("src.music.music_manager.MusicManager.set_volume", set_volume_mock)
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", sleep_mock)
        example_music_manager.volume = 55
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        await example_music_manager._play_track(group=group, track_list=track_list, track=track)
        get_track_path_mock.assert_called_once()
        media_player_mock.play.assert_called_once()
        wait_for_start_mock.assert_awaited_once()
        set_volume_mock.assert_awaited_once_with(example_music_manager.volume, set_global=False)
        assert is_playing_mock.call_count == 3  # is_playing becomes False at the 3rd call, so stop
        assert sleep_mock.await_count == 2  # Two times for while player is playing

    async def test_play_track_sets_start_time(self, example_music_manager, monkeypatch):
        """
        If a `Track` has the `start_at` attribute, the media player should skip to it.
        """
        media_player_mock = MagicMock()
        media_player_mock.is_playing.return_value = False
        monkeypatch.setattr("src.music.music_manager.vlc.MediaPlayer", MagicMock(return_value=media_player_mock))
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_path", MagicMock(return_value="url"))
        monkeypatch.setattr("src.music.music_manager.MusicManager._wait_for_current_player_to_be_playing",
                            CoroutineMock())
        monkeypatch.setattr("src.music.music_manager.MusicManager.set_volume", CoroutineMock())
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", CoroutineMock())
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        track.start_at = 1000
        await example_music_manager._play_track(group=group, track_list=track_list, track=track)
        media_player_mock.set_time.assert_called_once_with(1000)

    async def test_play_track_stops_at_end_time(self, example_music_manager, monkeypatch):
        """
        If a `Track` has the `end_at` attribute, the media player should stop if it is reached.
        """
        media_player_mock = MagicMock()
        media_player_mock.is_playing.return_value = True  # Can only exit if stop() is called

        def set_is_playing_to_false():
            media_player_mock.is_playing.return_value = False
        media_player_mock.get_time.return_value = 1000
        media_player_mock.stop = MagicMock(side_effect=set_is_playing_to_false)
        monkeypatch.setattr("src.music.music_manager.vlc.MediaPlayer", MagicMock(return_value=media_player_mock))
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_path", MagicMock(return_value="url"))
        monkeypatch.setattr("src.music.music_manager.MusicManager._wait_for_current_player_to_be_playing",
                            CoroutineMock())
        monkeypatch.setattr("src.music.music_manager.MusicManager.set_volume", CoroutineMock())
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", CoroutineMock())
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        track.end_at = 1000
        await example_music_manager._play_track(group=group, track_list=track_list, track=track)
        media_player_mock.get_time.assert_called_once()      # Compares get_time with track.end_at and
        assert media_player_mock.is_playing.call_count == 2  # immediately exits next step due to get_time >= end_at
        media_player_mock.stop.assert_called_once()          # and calls stop()

    async def test_wait_for_current_player_to_be_playing(self, example_music_manager, monkeypatch):
        """
        Wait until the current player is playing.
        """
        sleep_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", sleep_mock)
        example_music_manager._current_player = MagicMock()
        example_music_manager._current_player.is_playing = MagicMock(side_effect=[False, False, True])
        await example_music_manager._wait_for_current_player_to_be_playing()
        assert example_music_manager._current_player.is_playing.call_count == 3
        assert sleep_mock.await_count == 2

    def test_get_track_path_returns_audio_url_if_track_is_youtube_link(self, example_music_manager, monkeypatch):
        """
        If the `file` attribute of a `Track` is the link to a YouTube video, return the url of its audio stream.
        """
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        track.file = "https://www.youtube.com/watch?v=jIxas0a-KgM"
        pafy_mock = MagicMock()
        youtube_video_mock = MagicMock()
        audio_stream_mock = MagicMock()
        audio_stream_mock.url = "some-url"
        pafy_mock.new.return_value = youtube_video_mock
        youtube_video_mock.getbestaudio.return_value = audio_stream_mock
        monkeypatch.setattr("src.music.music_manager.pafy", pafy_mock)
        path = example_music_manager._get_track_path(group, track_list, track)
        assert path == "some-url"

    def test_get_track_path_raises_no_exceptions_if_youtube_link(self, example_music_manager):
        """
        This test does not use mocking and ensures that `pafy` and `youtube-dl` do not raise any exceptions when
        `_get_track_path()` is called and the `Track` is a link to a YouTube video.
        """
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        track.file = "https://www.youtube.com/watch?v=jIxas0a-KgM"
        example_music_manager._get_track_path(group, track_list, track)
        assert True  # Test is a success if no exception has been raised

    def test_get_track_path_returns_file_path_if_track_is_file(self, example_music_manager, monkeypatch):
        """
        If the `file` attribute of a `Track` is not the link to a YouTube video, return the file path.
        """
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        track.file = "file.mp3"
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_list_root_directory",
                            MagicMock(return_value="root/dir/"))
        monkeypatch.setattr("src.music.music_manager.os.path.isfile", lambda x: True)
        path = example_music_manager._get_track_path(group, track_list, track)
        assert path == "root/dir/file.mp3"

    def test_get_track_path_raises_value_error_if_root_directory_unknown(self, example_music_manager, monkeypatch):
        """
        If the `file` attribute of a `Track` is not the link to a YouTube video, return the file path. The file path
        consists of the root directory combined with the filename. If there is no root directory, raise a `ValueError`.
        """
        example_music_manager.directory = None
        group = example_music_manager.groups[0]
        group.directory = None
        track_list = group.track_lists[0]
        track_list.directory = None
        track = track_list.tracks[0]
        track.file = "file.mp3"
        with pytest.raises(ValueError):
            example_music_manager._get_track_path(group, track_list, track)

    def test_get_track_path_raises_value_error_if_path_is_not_existing_file(self, example_music_manager, monkeypatch):
        """
        If the `file` attribute of a `Track` is not the link to a YouTube video, return the file path. But if the file
        path does not refer to an existing file, raise a `ValueError`.
        """
        group = example_music_manager.groups[0]
        track_list = group.track_lists[0]
        track = track_list.tracks[0]
        track.file = "file.mp3"
        monkeypatch.setattr("src.music.music_manager.MusicManager._get_track_list_root_directory",
                            MagicMock(return_value="root/dir/"))  # non-existing dir
        with pytest.raises(ValueError):
            example_music_manager._get_track_path(group, track_list, track)

    def test_get_track_list_root_directory_returns_global_directory(self, example_music_manager):
        """
        If a directory is specified at the global level and no other level, return the global directory.
        """
        example_music_manager.directory = "global/dir"
        first_group = example_music_manager.groups[0]
        first_group.directory = None
        first_track_list_in_first_group = first_group.track_lists[0]
        first_track_list_in_first_group.directory = None
        directory = example_music_manager._get_track_list_root_directory(group=first_group,
                                                                         track_list=first_track_list_in_first_group)
        assert directory == "global/dir"

    def test_get_track_list_root_directory_returns_group_directory(self, example_music_manager):
        """
        If a directory is specified at the MusicGroup level and not the TrackList level, return the MusicGroup directory
        (even if there is a global directory specified).
        """
        example_music_manager.directory = "global/dir"
        first_group = example_music_manager.groups[0]
        first_group.directory = "group/dir"
        first_track_list_in_first_group = first_group.track_lists[0]
        first_track_list_in_first_group.directory = None
        directory = example_music_manager._get_track_list_root_directory(group=first_group,
                                                                         track_list=first_track_list_in_first_group)
        assert directory == "group/dir"

    def test_get_track_list_root_directory_returns_track_list_directory(self, example_music_manager):
        """
        If a directory is specified at the TrackList, return it (even if there is a global directory and a
        MusicGroup directory specified).
        """
        example_music_manager.directory = "global/dir"
        first_group = example_music_manager.groups[0]
        first_group.directory = "group/dir"
        first_track_list_in_first_group = first_group.track_lists[0]
        first_track_list_in_first_group.directory = "track/list/dir"
        directory = example_music_manager._get_track_list_root_directory(group=first_group,
                                                                         track_list=first_track_list_in_first_group)
        assert directory == "track/list/dir"

    def test_get_track_list_root_directory_raises_value_error_if_no_directory_on_any_level(self, example_music_manager):
        """
        If no directory is specified at all (neither the global, MusicGroup or TrackList level),
        then raise a ValueError.
        """
        example_music_manager.directory = None
        first_group = example_music_manager.groups[0]
        first_group.directory = None
        first_track_list_in_first_group = first_group.track_lists[0]
        first_track_list_in_first_group.directory = None
        with pytest.raises(ValueError):
            example_music_manager._get_track_list_root_directory(group=first_group,
                                                                 track_list=first_track_list_in_first_group)

    async def test_set_volume_sets_volume_if_global_parameter(self, example_music_manager):
        example_music_manager.volume = 0
        await example_music_manager.set_volume(volume=1, set_global=True)
        assert example_music_manager.volume == 1

    async def test_set_volume_does_not_set_volume_if_no_global_parameter(self, example_music_manager):
        example_music_manager.volume = 0
        await example_music_manager.set_volume(volume=1, set_global=False)
        assert example_music_manager.volume == 0

    async def test_set_volume_instantly_sets_player_volume_if_no_smooth_parameter(self, example_music_manager,
                                                                                  monkeypatch):
        sleep_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", sleep_mock)
        example_music_manager._current_player = MagicMock()
        await example_music_manager.set_volume(volume=1, smooth=False)
        sleep_mock.assert_not_awaited()
        example_music_manager._current_player.audio_set_volume.assert_called_once_with(1)

    async def test_set_volume_sets_player_volume_in_steps_if_smooth_parameter(self, example_music_manager, monkeypatch):
        sleep_mock = CoroutineMock()
        monkeypatch.setattr("src.music.music_manager.asyncio.sleep", sleep_mock)
        example_music_manager._current_player = MagicMock()
        example_music_manager._current_player.audio_get_volume.return_value = 0
        n_steps = 10
        seconds = 10
        await example_music_manager.set_volume(volume=100, smooth=True, n_steps=n_steps, seconds=seconds)
        sleep_mock.assert_awaited_with(seconds / n_steps)  # seconds / n_steps
        step_size = 100 / n_steps  # 1 = |starting_volume - new_volume|
        example_music_manager._current_player.audio_set_volume.assert_has_calls(
             [call(int((i + 1) * step_size)) for i in range(n_steps)]  # 10, 20, 30, ..., 100
        )
