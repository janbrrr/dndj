import pytest

from src.sound import Sound, SoundGroup


class TestSoundGroup:

    @pytest.fixture
    def minimal_sound_group_config(self):
        return {
            "name": "Some Name",
            "sounds": []
        }

    def test_minimal_dict_as_config(self, minimal_sound_group_config):
        sound_group = SoundGroup(minimal_sound_group_config)
        assert sound_group.name == "Some Name"
        assert len(sound_group.sounds) == 0

    def test_sounds_are_created(self, minimal_sound_group_config):
        sound_1_config = {
            "name": "Some Sound 1",
            "files": []
        }
        sound_2_config = {
            "name": "Some Sound 2",
            "files": []
        }
        minimal_sound_group_config["sounds"] = [
            sound_1_config,
            sound_2_config
        ]
        sound_group = SoundGroup(minimal_sound_group_config)
        assert len(sound_group.sounds) == 2
        assert sound_group.sounds[0] == Sound(sound_1_config)
        assert sound_group.sounds[1] == Sound(sound_2_config)

    def test_directory_is_none_by_default(self, minimal_sound_group_config):
        sound_group = SoundGroup(minimal_sound_group_config)
        assert sound_group.directory is None

    def test_directory_in_config(self, minimal_sound_group_config):
        minimal_sound_group_config["directory"] = "/some/dir/"
        sound_group = SoundGroup(minimal_sound_group_config)
        assert sound_group.directory == "/some/dir/"

    def test_sounds_are_sorted_by_name_by_default(self, minimal_sound_group_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "files": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "files": []
        }
        minimal_sound_group_config["sounds"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        sound_group = SoundGroup(minimal_sound_group_config)
        assert sound_group.sounds[0] == Sound(name_starts_with_a_config)
        assert sound_group.sounds[1] == Sound(name_starts_with_n_config)

    def test_sort_in_config(self, minimal_sound_group_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "files": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "files": []
        }
        minimal_sound_group_config["sort"] = False
        minimal_sound_group_config["sounds"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        sound_group = SoundGroup(minimal_sound_group_config)
        assert sound_group.sounds[0] == Sound(name_starts_with_n_config)
        assert sound_group.sounds[1] == Sound(name_starts_with_a_config)

    def test_sounds_use_tuple_instead_of_list(self, minimal_sound_group_config):
        sound_group = SoundGroup(minimal_sound_group_config)
        assert isinstance(sound_group.sounds, tuple)

    def test_equal_if_same_config(self):
        group_1 = SoundGroup({
            "name": "Group",
            "sounds": []
        })
        group_2 = SoundGroup({
            "name": "Group",
            "sounds": []
        })
        assert group_1 == group_2
        assert group_2 == group_1

    def test_not_equal_if_different_attributes(self):
        group_1 = SoundGroup({
            "name": "Unique Group",
            "sounds": []
        })
        group_2 = SoundGroup({
            "name": "Normal Group",
            "sounds": []
        })
        assert group_1 != group_2
        assert group_2 != group_1

    def test_not_equal_if_different_number_of_sounds(self):
        group_1 = SoundGroup({
            "name": "Group",
            "sounds": []
        })
        group_2 = SoundGroup({
            "name": "Group",
            "sounds": [{
                "name": "Sound",
                "files": []
            }]
        })
        assert group_1 != group_2
        assert group_2 != group_1

    def test_not_equal_if_different_sounds(self):
        group_1 = SoundGroup({
            "name": "Group",
            "sounds": [{
                "name": "Unique Sound",
                "files": []
            }]
        })
        group_2 = SoundGroup({
            "name": "Group",
            "sounds": [{
                "name": "Other Sound",
                "files": []
            }]
        })
        assert group_1 != group_2
        assert group_2 != group_1

    def test_not_equal_if_different_types(self):
        config = {
            "name": "Group",
            "sounds": [{
                "name": "Sound",
                "files": []
            }]
        }
        group = SoundGroup(config)
        assert config != group
        assert group != config
