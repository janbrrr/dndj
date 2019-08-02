import asyncio
import json
from unittest.mock import MagicMock

import pytest
from asynctest import CoroutineMock

from src.music import MusicManager
from src.server import Server
from src.sound import SoundManager


class TestServer:
    @pytest.fixture
    def minimal_server_config_file(self, tmp_path):
        content = """
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
        return Server(config_path=minimal_server_config_file, host="127.0.0.1", port=8080)

    @pytest.fixture
    async def minimal_client(self, minimal_server, aiohttp_client):
        app = await minimal_server._init_app()
        client = await aiohttp_client(app)
        return client

    @pytest.fixture
    def patched_example_server(self, example_config_str, tmp_path, monkeypatch):
        example_config_file = tmp_path / "config.yaml"
        example_config_file.write_text(example_config_str)
        monkeypatch.setattr(MusicManager, "_play_track", CoroutineMock())
        monkeypatch.setattr(SoundManager, "_play_sound_file", CoroutineMock())
        with monkeypatch.context() as m:
            m.setattr("src.music.music_manager.MusicChecker", MagicMock())
            m.setattr("src.sound.sound_manager.SoundChecker", MagicMock())
            server = Server(config_path=example_config_file, host="127.0.0.1", port=8080)
        return server

    @pytest.fixture
    async def patched_example_client(self, patched_example_server, aiohttp_client):
        app = await patched_example_server._init_app()
        client = await aiohttp_client(app)
        return client

    def test_minimal_server_configures_music(self, minimal_server):
        minimal_music_config = {"volume": 0.2, "groups": []}
        assert minimal_server.music == MusicManager(minimal_music_config)

    def test_minimal_server_configures_sound(self, minimal_server):
        minimal_sound_config = {"volume": 1, "groups": []}
        assert minimal_server.sound == SoundManager(minimal_sound_config)

    async def test_client_can_access_index(self, minimal_client):
        resp = await minimal_client.get("/")
        assert resp.status == 200

    async def test_client_can_connect_via_websocket_to_server(self, minimal_client):
        ws_resp = await minimal_client.ws_connect("/")
        assert ws_resp.closed is False

    async def test_client_can_request_music_to_play(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        play_music_request = {"action": "playMusic", "groupIndex": 0, "trackListIndex": 1}
        await ws_resp.send_str(json.dumps(play_music_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "nowPlaying",
            "groupIndex": 0,
            "trackListIndex": 1,
            "groupName": "Scene 1 - Travel",
            "trackName": "Forest Music",
        }

    async def test_client_can_request_music_to_stop(self, patched_example_client, monkeypatch):
        # Mock playing the music with sleeping to keep the task alive such that the client can cancel it
        monkeypatch.setattr(MusicManager, "_play_track", CoroutineMock(return_value=asyncio.sleep(5)))
        ws_resp = await patched_example_client.ws_connect("/")
        play_music_request = {"action": "playMusic", "groupIndex": 0, "trackListIndex": 1}
        await ws_resp.send_str(json.dumps(play_music_request))
        resp = await ws_resp.receive()  # Receive message that the music started playing
        stop_music_request = {"action": "stopMusic"}
        await ws_resp.send_str(json.dumps(stop_music_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {"action": "musicStopped"}

    async def test_client_can_set_music_master_volume(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_music_master_volume_request = {"action": "setMusicMasterVolume", "volume": 0.75}
        await ws_resp.send_str(json.dumps(set_music_master_volume_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {"action": "setMusicMasterVolume", "volume": 0.75}

    async def test_client_can_request_sound_to_play(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        play_sound_request = {"action": "playSound", "groupIndex": 0, "soundIndex": 0}
        await ws_resp.send_str(json.dumps(play_sound_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "soundPlaying",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 1,
            "loop": False,
            "loopDelay": "0",
        }

    async def test_client_is_notified_when_sound_finishes(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        play_sound_request = {"action": "playSound", "groupIndex": 0, "soundIndex": 0}
        await ws_resp.send_str(json.dumps(play_sound_request))
        _ = await ws_resp.receive()  # First message is that the sound started playing
        resp = await ws_resp.receive()  # Second message is that the sound finished playing
        assert json.loads(resp.data) == {
            "action": "soundFinished",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 1,
            "loop": False,
            "loopDelay": "0",
        }

    async def test_client_can_request_sound_to_stop(self, patched_example_client, monkeypatch):
        # Mock playing the sound with sleeping to keep the task alive such that the client can cancel it
        monkeypatch.setattr(SoundManager, "_play_sound_file", CoroutineMock(return_value=asyncio.sleep(5)))
        ws_resp = await patched_example_client.ws_connect("/")
        play_sound_request = {"action": "playSound", "groupIndex": 0, "soundIndex": 0}
        await ws_resp.send_str(json.dumps(play_sound_request))
        stop_sound_request = {"action": "stopSound", "groupIndex": 0, "soundIndex": 0}
        await ws_resp.send_str(json.dumps(stop_sound_request))
        _ = await ws_resp.receive()  # First message is that the sound started playing
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "soundStopped",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 1,
            "loop": False,
            "loopDelay": "0",
        }

    async def test_client_can_request_sound_to_stop_that_is_waiting_for_next_loop(
        self, patched_example_server, aiohttp_client, monkeypatch
    ):
        """
        Test that a sound that has `loop` set with a high `loop_delay` will stop and notify the client that the
        (looping) sound has been stopped.
        """
        sound = patched_example_server.sound.groups[0].sounds[0]
        sound.loop = True
        sound.loop_delay = 42000  # 42 sec
        app = await patched_example_server._init_app()
        client = await aiohttp_client(app)
        ws_resp = await client.ws_connect("/")
        play_sound_request = {"action": "playSound", "groupIndex": 0, "soundIndex": 0}
        await ws_resp.send_str(json.dumps(play_sound_request))
        await asyncio.sleep(0.5)  # Make sure the sound has been played and is now waiting for the next replay
        _ = await ws_resp.receive()  # Receive message that the sound started playing
        stop_sound_request = {"action": "stopSound", "groupIndex": 0, "soundIndex": 0}
        await ws_resp.send_str(json.dumps(stop_sound_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "soundStopped",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 1,
            "loop": True,
            "loopDelay": "42000",  # Remember that loop_delay was set
        }

    async def test_client_can_set_sound_master_volume(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_sound_master_volume_request = {"action": "setSoundMasterVolume", "volume": 0.25}
        await ws_resp.send_str(json.dumps(set_sound_master_volume_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {"action": "setSoundMasterVolume", "volume": 0.25}

    async def test_client_can_set_sound_volume(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_sound_volume_request = {"action": "setSoundVolume", "groupIndex": 0, "soundIndex": 0, "volume": 0.25}
        await ws_resp.send_str(json.dumps(set_sound_volume_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "setSoundVolume",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 0.25,
            "loop": False,
            "loopDelay": "0",
        }

    async def test_client_can_set_sound_loop(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_sound_loop_request = {"action": "setSoundLoop", "groupIndex": 0, "soundIndex": 0, "loop": True}
        await ws_resp.send_str(json.dumps(set_sound_loop_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "setSoundLoop",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 1,
            "loop": True,
            "loopDelay": "0",
        }

    async def test_client_can_set_sound_loop_delay_to_single_number(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_loop_delay_request = {"action": "setSoundLoopDelay", "groupIndex": 0, "soundIndex": 0, "loopDelay": "24"}
        await ws_resp.send_str(json.dumps(set_loop_delay_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "setSoundLoopDelay",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 1,
            "loop": False,
            "loopDelay": "24",
        }

    async def test_client_can_set_sound_loop_delay_to_interval(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_loop_delay_request = {"action": "setSoundLoopDelay", "groupIndex": 0, "soundIndex": 0, "loopDelay": "24-42"}
        await ws_resp.send_str(json.dumps(set_loop_delay_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "setSoundLoopDelay",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 1,
            "loop": False,
            "loopDelay": "24-42",
        }

    async def test_client_cannot_set_sound_loop_delay_to_invalid_value(self, patched_example_client):
        ws_resp = await patched_example_client.ws_connect("/")
        set_loop_delay_request = {"action": "setSoundLoopDelay", "groupIndex": 0, "soundIndex": 0, "loopDelay": "24-?"}
        await ws_resp.send_str(json.dumps(set_loop_delay_request))
        resp = await ws_resp.receive()
        assert json.loads(resp.data) == {
            "action": "setSoundLoopDelay",
            "groupIndex": 0,
            "soundIndex": 0,
            "groupName": "Footsteps",
            "soundName": "Footsteps on Dry Leaves",
            "volume": 1,
            "loop": False,
            "loopDelay": "0",  # Nothing changed!
        }
