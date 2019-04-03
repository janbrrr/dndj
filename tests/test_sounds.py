import pytest

from src.sounds import SoundFile, Sound, SoundGroup, SoundManager


class TestSoundFile:

    def test_str_as_config(self):
        sound_file = SoundFile("some-filename.wav")
        assert sound_file.file == "some-filename.wav"

    def test_minimal_dict_as_config(self):
        config = {
            "file": "some-filename.wav"
        }
        sound_file = SoundFile(config)
        assert sound_file.file == "some-filename.wav"

    def test_end_at_is_none_by_default(self):
        sound_file = SoundFile("some-filename.wav")
        assert sound_file.end_at is None
        config = {
            "file": "some-filename.wav"
        }
        sound_file = SoundFile(config)
        assert sound_file.end_at is None

    def test_end_at_is_computed_correctly(self):
        config = {
            "file": "some-filename.wav",
            "end_at": "1:10:42"
        }
        end_at_in_ms = (42 + 10*60 + 1*60*60) * 1000
        sound_file = SoundFile(config)
        assert sound_file.end_at == end_at_in_ms

    def test_non_wav_or_ogg_raises_type_error(self):
        with pytest.raises(TypeError):
            SoundFile("some-filename.notwavorogg")

    def test_accepts_wav_and_ogg_files(self):
        SoundFile("some-filename.wav")
        SoundFile("some-filename.ogg")


class TestSound:

    @pytest.fixture
    def minimal_sound_config(self):
        return {
            "name": "Some Name",
            "files": []
        }

    def test_minimal_dict_as_config(self, minimal_sound_config):
        sound = Sound(minimal_sound_config)
        assert sound.name == "Some Name"
        assert len(sound.files) == 0

    def test_sounds_are_created(self, minimal_sound_config):
        minimal_sound_config["files"] = [
            "some-filename.wav",
            "other-filename.wav"
        ]
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

    def test_files_use_tuple_instead_of_list(self, minimal_sound_config):
        sound = Sound(minimal_sound_config)
        assert isinstance(sound.files, tuple)


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


class TestSoundManager:

    @pytest.fixture
    def minimal_sound_manager_config(self):
        return {
            "volume": 1,
            "groups": []
        }

    def test_minimal_dict_as_config(self, minimal_sound_manager_config):
        sound_manager = SoundManager(minimal_sound_manager_config, mixer=None)
        assert sound_manager.volume == 1
        assert len(sound_manager.groups) == 0

    def test_groups_are_created(self, minimal_sound_manager_config):
        sound_group_1_config = {
            "name": "Some Sound Group 1",
            "sounds": []
        }
        sound_group_2_config = {
            "name": "Some Sound Group 2",
            "sounds": []
        }
        minimal_sound_manager_config["groups"] = [
            sound_group_1_config,
            sound_group_2_config
        ]
        sound_manager = SoundManager(minimal_sound_manager_config, mixer=None)
        assert len(sound_manager.groups) == 2
        assert sound_manager.groups[0] == SoundGroup(sound_group_1_config)
        assert sound_manager.groups[1] == SoundGroup(sound_group_2_config)

    def test_directory_is_none_by_default(self, minimal_sound_manager_config):
        sound_manager = SoundManager(minimal_sound_manager_config, mixer=None)
        assert sound_manager.directory is None

    def test_directory_in_config(self, minimal_sound_manager_config):
        minimal_sound_manager_config["directory"] = "/some/dir/"
        sound_manager = SoundManager(minimal_sound_manager_config, mixer=None)
        assert sound_manager.directory == "/some/dir/"

    def test_groups_are_sorted_by_name_by_default(self, minimal_sound_manager_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "sounds": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "sounds": []
        }
        minimal_sound_manager_config["groups"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        sound_manager = SoundManager(minimal_sound_manager_config, mixer=None)
        assert sound_manager.groups[0] == SoundGroup(name_starts_with_a_config)
        assert sound_manager.groups[1] == SoundGroup(name_starts_with_n_config)

    def test_sort_in_config(self, minimal_sound_manager_config):
        name_starts_with_n_config = {
            "name": "Not First In The Alphabet",
            "sounds": []
        }
        name_starts_with_a_config = {
            "name": "Alphabet",
            "sounds": []
        }
        minimal_sound_manager_config["sort"] = False
        minimal_sound_manager_config["groups"] = [
            name_starts_with_n_config,
            name_starts_with_a_config
        ]
        sound_manager = SoundManager(minimal_sound_manager_config, mixer=None)
        assert sound_manager.groups[0] == SoundGroup(name_starts_with_n_config)
        assert sound_manager.groups[1] == SoundGroup(name_starts_with_a_config)

    def test_sound_groups_use_tuple_instead_of_list(self, minimal_sound_manager_config):
        sound_manager = SoundManager(minimal_sound_manager_config, mixer=None)
        assert isinstance(sound_manager.groups, tuple)
