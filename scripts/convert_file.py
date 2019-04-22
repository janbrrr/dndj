import os
import argparse

import pydub


def convert_file(file_path, _format, start=None, end=None, out=None):
    filename, file_extension = os.path.splitext(file_path)
    audio = pydub.audio_segment.AudioSegment.from_file(file_path)
    if start is not None:
        start = int(start)
        audio = audio[start:]
    if end is not None:
        end = int(end)
        audio = audio[:end]
    if out is not None:
        head, tail = os.path.split(file_path)
        audio.export(os.path.join(head, f"{out}.{_format}"), format=_format)
    else:
        audio.export(f"{filename}.{_format}", format=_format)


if __name__ == "__main__":
    """
    Converts a file (e.g., mp3) to a different format (e.g., wav, ogg). The converted file will be in the same 
    directory as the original file. Can convert a single file or every file in a directory.
    
    Run this script as follows:
    `python convert_file.py filename-or-directory format`
    
    Example:
    `python convert_file.py my_sound.wav ogg
    
    This script supports additional arguments, type `python convert_file.py --help` for more information.
    """
    parser = argparse.ArgumentParser(description="Perform a file conversion")
    parser.add_argument("source", metavar="S", help="path to the source (file or directory)")
    parser.add_argument("format", metavar="F", help="new file format")
    parser.add_argument("--start", required=False, help="start file at time in milliseconds")
    parser.add_argument("--end", required=False, help="end file at time in milliseconds")
    parser.add_argument("--out", required=False, help="output name (excluding extension)")
    args = parser.parse_args()

    if os.path.isdir(args.source):
        for file in os.listdir(args.source):
            full_file_path = os.path.join(args.source, file)
            if os.path.isfile(full_file_path):
                convert_file(file_path=full_file_path, _format=args.format)
    else:
        convert_file(file_path=args.source, _format=args.format, start=args.start, end=args.end, out=args.out)
