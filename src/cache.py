import hashlib
import json
import os
from typing import List


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CACHE_DIR = os.path.join(BASE_DIR, ".dndj_cache")
CONVERSION_CACHE_DIR = os.path.join(CACHE_DIR, "conversions")

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
if not os.path.exists(CONVERSION_CACHE_DIR):
    os.makedirs(CONVERSION_CACHE_DIR)


def save_list(content: List, filename: str):
    with open(os.path.join(CACHE_DIR, filename), "w") as file:
        json.dump(content, file, indent=4)


def load_list(filename: str) -> List:
    path = os.path.join(CACHE_DIR, filename)
    content = []
    if os.path.exists(path):
        with open(path, "r") as file:
            content = json.load(file)
    return content


def get_file_hash(file_path) -> str:
    sha256_hash = hashlib.sha3_256()
    with open(file_path, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def exists_converted_file(filename) -> bool:
    return os.path.exists(os.path.join(CONVERSION_CACHE_DIR, filename))
