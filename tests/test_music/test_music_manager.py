import pytest

from src.music import MusicGroup, MusicManager


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
