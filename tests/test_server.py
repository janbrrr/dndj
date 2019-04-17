import json
import pytest
from unittest.mock import MagicMock
from asynctest import CoroutineMock

from src.music import MusicManager
from src.server import Server
from src.sound import SoundManager


class TestServer:

    @pytest.fixture
    def minimal_server_config_file(self, tmp_path):
        content = """---
        music:
          volume: 0.2
          groups: []
        sound:
          volume: 1
          groups: []
        """
        config_file = tmp_path / "config.yaml"
        config_file.write_text(content)
        return config_file

    @pytest.fixture
    def minimal_server(self, minimal_server_config_file):
        return Server(
            config_path=minimal_server_config_file,
            host="127.0.0.1",
            port=8080
        )

    @pytest.fixture
    async def minimal_client(self, minimal_server, aiohttp_client):
        app = await minimal_server._init_app()
        client = await aiohttp_client(app)
        return client

    @pytest.fixture
    def patched_example_server(self, monkeypatch):
        monkeypatch.setattr(MusicManager, "play_track_list", CoroutineMock())
        monkeypatch.setattr(MusicManager, "cancel", CoroutineMock())
        monkeypatch.setattr(MusicManager, "set_volume", CoroutineMock())
        monkeypatch.setattr(SoundManager, "play_sound", CoroutineMock())
        monkeypatch.setattr(SoundManager, "set_volume", MagicMock())
        return Server(
            config_path="example/config.yaml",
            host="127.0.0.1",
            port=8080
        )

    @pytest.fixture
    async def patched_example_client(self, patched_example_server, aiohttp_client):
        app = await patched_example_server._init_app()
        client = await aiohttp_client(app)
        return client

    def test_minimal_server_configures_music(self, minimal_server):
        minimal_music_config = {
            "volume": 0.2,
            "groups": []
        }
        assert minimal_server.music == MusicManager(minimal_music_config)

    def test_minimal_server_configures_sound(self, minimal_server):
        minimal_sound_config = {
            "volume": 1,
            "groups": []
        }
        assert minimal_server.sound == SoundManager(minimal_sound_config)

    async def test_client_can_access_index(self, minimal_client):
        resp = await minimal_client.get('/')
        assert resp.status == 200

    async def test_client_can_connect_via_websocket_to_server(self, minimal_client):
        ws_resp = await minimal_client.ws_connect("/")
        assert ws_resp.closed is False

    async def test_client_can_request_music_to_play(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        play_music_request = {
            "action": "playMusic",
            "groupIndex": 0,
            "trackListIndex": 1
        }
        await ws_resp.send_str(json.dumps(play_music_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {"action": "nowPlaying", "groupIndex": 0,
                                         "trackListIndex": 1, "groupName": "Scene 1 - Travel",
                                         "trackName": "Forest Music"}

    async def test_client_can_request_music_to_stop(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        stop_music_request = {
            "action": "stopMusic"
        }
        await ws_resp.send_str(json.dumps(stop_music_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {"action": "musicStopped"}

    async def test_client_can_set_music_volume(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_music_volume_request = {
            "action": "setMusicVolume",
            "volume": 0.75
        }
        await ws_resp.send_str(json.dumps(set_music_volume_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {"action": "setMusicVolume", "volume": 0.75}

    async def test_client_can_request_sound_to_play(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        play_sound_request = {
            "action": "playSound",
            "groupIndex": 0,
            "soundIndex": 0
        }
        await ws_resp.send_str(json.dumps(play_sound_request))
        await ws_resp.close()

    async def test_client_can_set_sound_volume(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_sound_volume_request = {
            "action": "setSoundVolume",
            "volume": 0.25
        }
        await ws_resp.send_str(json.dumps(set_sound_volume_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {"action": "setSoundVolume", "volume": 0.25}