import pytest

from src.music import MusicManager
from src.server import Server
from src.sounds import SoundManager


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

    def test_minimal_server_configures_music(self, minimal_server):
        minimal_music_config = {
            "volume": 0.2,
            "groups": []
        }
        assert minimal_server.music == MusicManager(minimal_music_config,
                                                    music_mixer=minimal_server.music.music_mixer)

    def test_minimal_server_configures_sound(self, minimal_server):
        minimal_sound_config = {
            "volume": 1,
            "groups": []
        }
        assert minimal_server.sound == SoundManager(minimal_sound_config,
                                                    mixer=minimal_server.sound.mixer)

    async def test_minimal_server_app_runs(self, minimal_server, aiohttp_server):
        app = await minimal_server._init_app()
        server = await aiohttp_server(app)
        await server.close()

    async def test_client_can_connect_to_minimal_server_app(self, minimal_server, aiohttp_client):
        app = await minimal_server._init_app()
        client = await aiohttp_client(app)
        resp = await client.get('/')
        assert resp.status == 200
