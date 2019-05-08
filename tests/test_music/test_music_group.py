import pytest

from src.music import TrackList, MusicGroup


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

    def test_equal_if_same_config(self):
        group_1 = MusicGroup({
            "name": "Group",
            "track_lists": []
        })
        group_2 = MusicGroup({
            "name": "Group",
            "track_lists": []
        })
        assert group_1 == group_2
        assert group_2 == group_1

    def test_not_equal_if_different_attributes(self):
        group_1 = MusicGroup({
            "name": "Group",
            "track_lists": []
        })
        group_2 = MusicGroup({
            "name": "Group",
            "directory": "/some/dir/",
            "track_lists": []
        })
        assert group_1 != group_2
        assert group_2 != group_1

    def test_not_equal_if_different_number_of_track_lists(self):
        group_1 = MusicGroup({
            "name": "Group",
            "track_lists": []
        })
        group_2 = MusicGroup({
            "name": "Group",
            "track_lists": [{
                "name": "Some Name",
                "tracks": []
            }]
        })
        assert group_1 != group_2
        assert group_2 != group_1

    def test_not_equal_if_different_track_lists(self):
        group_1 = MusicGroup({
            "name": "Group",
            "track_lists": [{
                "name": "Some Name",
                "tracks": []
            }]
        })
        group_2 = MusicGroup({
            "name": "Group",
            "track_lists": [{
                "name": "Different Name",
                "tracks": []
            }]
        })
        assert group_1 != group_2
        assert group_2 != group_1

    def test_not_equal_if_different_types(self):
        config = {
            "name": "Group",
            "track_lists": []
        }
        group = MusicGroup(config)
        assert config != group
        assert group != config
