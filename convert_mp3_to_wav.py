import sys

import pydub


if __name__ == "__main__":
    """
    Converts an `.mp3` file to a `.wav` file. The `.wav` will be in the same directory as the `.mp3` file.
    Run this script as follows:
    `python convert_mp3_to_wav.py filename.mp3`
    """
    source = sys.argv[1]
    name = source.split(".mp3")[0]
    audio = pydub.audio_segment.AudioSegment.from_mp3(source)
    audio.export(f"{name}.wav", format="wav")
