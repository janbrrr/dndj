import pytest

from src.music import Track, TrackList, MusicGroup, MusicManager


class TestTrack:

    def test_str_as_config(self):
        track = Track("some-filename.mp3")
        assert track.file == "some-filename.mp3"

    def test_minimal_dict_as_config(self):
        config = {
            "file": "some-filename.mp3"
        }
        track = Track(config)
        assert track.file == "some-filename.mp3"

    def test_start_at_is_none_by_default(self):
        track = Track("some-filename.mp3")
        assert track.start_at is None
        config = {
            "file": "some-filename.mp3"
        }
        track = Track(config)
        assert track.start_at is None

    def test_start_at_is_computed_correctly(self):
        config = {
            "file": "some-filename.mp3",
            "start_at": "1:10:42"
        }
        start_at_in_ms = (42 + 10*60 + 1*60*60) * 1000
        track = Track(config)
        assert track.start_at == start_at_in_ms

    def test_non_mp3_raises_type_error(self):
        with pytest.raises(TypeError):
            Track("some-filename.notmp3")


class TestTrackList:

    @pytest.fixture
    def minimal_track_list_config(self):
        return {
            "name": "Some Name",
            "tracks": []
        }

    def test_minimal_dict_as_config(self, minimal_track_list_config):
        track_list = TrackList(minimal_track_list_config)
        assert track_list.name == "Some Name"
        assert len(track_list.tracks) == 0

    def test_tracks_are_created(self, minimal_track_list_config):
        minimal_track_list_config["tracks"] = [
            "some-filename.mp3",
            "other-filename.mp3"
        ]
        track_list = TrackList(minimal_track_list_config)
        assert len(track_list.tracks) == 2
        assert track_list.tracks[0] == Track("some-filename.mp3")
        assert track_list.tracks[1] == Track("other-filename.mp3")

    def test_directory_is_none_by_default(self, minimal_track_list_config):
        track_list = TrackList(minimal_track_list_config)
        assert track_list.directory is None

    def test_directory_in_config(self, minimal_track_list_config):
        minimal_track_list_config["directory"] = "/some/dir/"
        track_list = TrackList(minimal_track_list_config)
        assert track_list.directory == "/some/dir/"

    def test_loop_is_true_by_default(self, minimal_track_list_config):
        track_list = TrackList(minimal_track_list_config)
        assert track_list.loop is True

    def test_loop_in_config(self, minimal_track_list_config):
        minimal_track_list_config["loop"] = False
        track_list = TrackList(minimal_track_list_config)
        assert track_list.loop is False

    def test_shuffle_is_true_by_default(self, minimal_track_list_config):
        track_list = TrackList(minimal_track_list_config)
        assert track_list.shuffle is True

    def test_shuffle_in_config(self, minimal_track_list_config):
        minimal_track_list_config["shuffle"] = False
        track_list = TrackList(minimal_track_list_config)
        assert track_list.shuffle is False

    def test_tracks_use_tuple_instead_of_list(self, minimal_track_list_config):
        track_list = TrackList(minimal_track_list_config)
        assert isinstance(track_list.tracks, tuple)


class TestMusicGroup:

    @pytest.fixture
    def minimal_music_group_config(self):
        return {
            "name": "Some Name",
            "track_lists": []
        }

    def test_minimal_dict_as_config(self, minimal_music_group_config):
        music_group = MusicGroup(minimal_music_group_config)
        assert music_group.name == "Some Name"
        assert len(music_group.track_lists) == 0

    def test_track_lists_are_created(self, minimal_music_group_config):
        track_list_1_config = {
            "name": "Some Track List 1",
            "tracks": []
        }
        track_list_2_config = {
            "name": "Some Track List 2",
            "tracks": []
        }
        minimal_music_group_config["track_lists"] = [
            track_list_1_config,
            track_list_2_config
        ]
        music_group = MusicGroup(minimal_music_group_config)
        assert len(music_group.track_lists) == 2
        assert music_group.track_lists[0] == TrackList(track_list_1_config)
        assert music_group.track_lists[1] == TrackList(track_list_2_config)

    def test_directory_is_none_by_default(self, minimal_music_group_config):
        music_group = MusicGroup(minimal_music_group_config)
        assert music_group.directory is None

    def test_directory_in_config(self, minimal_music_group_config):
        minimal_music_group_config["directory"] = "/some/dir/"
        music_group = MusicGroup(minimal_music_group_config)
        assert music_group.directory == "/some/dir/"

    def test_tracks_lists_are_sorted_by_name_by_default(self, minimal_music_group_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "tracks": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "tracks": []
        }
        minimal_music_group_config["track_lists"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        music_group = MusicGroup(minimal_music_group_config)
        assert music_group.track_lists[0] == TrackList(name_starts_with_a_config)
        assert music_group.track_lists[1] == TrackList(name_starts_with_n_config)

    def test_sort_in_config(self, minimal_music_group_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "tracks": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "tracks": []
        }
        minimal_music_group_config["sort"] = False
        minimal_music_group_config["track_lists"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        music_group = MusicGroup(minimal_music_group_config)
        assert music_group.track_lists[0] == TrackList(name_starts_with_n_config)
        assert music_group.track_lists[1] == TrackList(name_starts_with_a_config)

    def test_track_lists_use_tuple_instead_of_list(self, minimal_music_group_config):
        music_group = MusicGroup(minimal_music_group_config)
        assert isinstance(music_group.track_lists, tuple)


class TestMusicManager:

    @pytest.fixture
    def minimal_music_manager_config(self):
        return {
            "volume": 50,
            "groups": []
        }

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
