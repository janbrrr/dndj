from src.check_version import check_youtube_dl_version


def test_check_youtube_dl_version():
    """
    This test will fail if a new version of `youtube-dl` is available.
    This test should always succeed at the CI step, because the latest version will be installed during a run.
    """
    assert check_youtube_dl_version()
