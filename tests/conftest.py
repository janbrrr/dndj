import pytest
import yaml

from src.loader import CustomLoader


@pytest.fixture(scope="session")
def example_config_str():
    config = """
    music:
      volume: 20
      groups:
      - name: Scene 1 - Travel
        directory: "path/to/scene-1"
        track_lists:
        - name: Forest Music
          tracks:
          - forest-music-1.mp3
          - forest-music-2.mp3
        - name: Battle Music
          tracks:
          - https://www.youtube.com/watch?v=jIxas0a-KgM  # Strength of a Thousand Men
          - https://www.youtube.com/watch?v=U6K-ZeqpO8k  # Victory
      - name: Scene 2 - Arrival
        track_lists:
        - name: City Music
          tracks:
          - https://www.youtube.com/watch?v=_52K0E_gNY0  # Medieval City
        - name: Tavern Music
          tracks:
          - https://www.youtube.com/watch?v=uaX-2RMzVvQ  # Heroes Inn
    sound:
      volume: 1
      directory: "path/to/sounds"
      groups:
        - name: Footsteps
          sounds:
          - name: Footsteps on Dry Leaves
            files:
            - file: footsteps-dry-leaves.wav
              end_at: 0:0:4
          - name: Footsteps on Wood Branches
            files:
            - file: steps-on-a-wood-branch.ogg
              end_at: 0:0:5
    """
    return config


@pytest.fixture
def example_config(example_config_str):
    return yaml.load(example_config_str, Loader=CustomLoader)
