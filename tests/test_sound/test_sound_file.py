import pytest

from src.sound import SoundFile


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
