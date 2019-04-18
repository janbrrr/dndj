from src.music import Track


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

    def test_end_at_is_computed_correctly(self):
        config = {
            "file": "some-filename.mp3",
            "end_at": "1:10:42"
        }
        end_at_in_ms = (42 + 10*60 + 1*60*60) * 1000
        track = Track(config)
        assert track.end_at == end_at_in_ms

    def test_is_youtube_link_returns_true_for_a_youtube_link(self):
        track = Track("https://www.youtube.com/watch?v=jIxas0a-KgM")
        assert track.is_youtube_link is True

    def test_is_youtube_link_returns_false_for_a_file(self):
        track = Track("some-file.mp3")
        assert track.is_youtube_link is False
