import logging

import pkg_resources
import requests


logger = logging.getLogger(__name__)


def check_youtube_dl_version() -> bool:
    """
    Returns `False` if a new version of the 'youtube-dl' package is available.
    If that is the case, this information will be logged.
    """
    result = requests.get("https://pypi.org/pypi/youtube_dl/json")
    latest_version = result.json()["info"]["version"]
    current_version = pkg_resources.get_distribution("youtube-dl").version
    is_latest_version = current_version == latest_version
    if not is_latest_version:
        logger.warning("A new version of the 'youtube-dl' package is available.")
        logger.warning("YouTube support may not work if the package is not updated.")
        logger.warning("Type 'pip install --upgrade youtube-dl' to update it.")
    return is_latest_version
