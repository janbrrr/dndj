import json
import os
from typing import List


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CACHE_DIR = os.path.join(BASE_DIR, ".dndj_cache")


def create_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def save(content: List, filename: str):
    create_cache_dir()
    with open(os.path.join(CACHE_DIR, filename), "w") as file:
        json.dump(content, file, indent=4)


def load(filename: str) -> List:
    path = os.path.join(CACHE_DIR, filename)
    content = []
    if os.path.exists(path):
        with open(path, "r") as file:
            content = json.load(file)
    return content
