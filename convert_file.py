import os
import argparse

import pydub


if __name__ == "__main__":
    """
    Converts a file (e.g., mp3) to a different format (e.g., wav, ogg). The converted file will be in the same 
    directory as the original file. Can convert a single file or every file in a directory.
    
    Run this script as follows:
    `python convert_file.py filename-or-directory format`
    """
    parser = argparse.ArgumentParser(description="Perform a file conversion")
    parser.add_argument("source", metavar="S", help="path to the source (file or directory)")
    parser.add_argument("format", metavar="F", help="new file format")
    args = parser.parse_args()

    if os.path.isdir(args.source):
        for file in os.listdir(args.source):
            full_file_path = os.path.join(args.source, file)
            if os.path.isfile(full_file_path):
                filename, file_extension = os.path.splitext(full_file_path)
                audio = pydub.audio_segment.AudioSegment.from_file(full_file_path)
                audio.export(f"{filename}.{args.format}", format=args.format)
    else:
        filename, file_extension = os.path.splitext(args.source)
        audio = pydub.audio_segment.AudioSegment.from_file(args.source)
        audio.export(f"{filename}.{args.format}", format=args.format)
