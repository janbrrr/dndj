import json
import logging
import pathlib

import pygame.mixer as mixer
import jinja2

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_response import Response

from src.music import MusicManager
from src.sounds import SoundManager

logging.basicConfig(format='%(levelname)-6s: %(message)s', level=logging.DEBUG)

PROJECT_ROOT = pathlib.Path(__file__).parent


class Server:
    STATE_SCENE_SELECTION = 0
    STATE_SOUND_SELECTION = 1

    SLEEP_TIME = 0.01

    def __init__(self, config_path):
        mixer.init()
        with open(config_path) as config_file:
            config = json.load(config_file)
        self.music = MusicManager(config["music"], mixer.music)
        self.sound = SoundManager(config["sound"], mixer)
        self.app = None

    def start(self):
        """
        Starts the web server.
        """
        host = "127.0.0.1"
        port = 8080
        self.app = self._init_app()
        logging.info(f'Server started on http://{host}:{port}')
        web.run_app(self.app, host=host, port=port)

    async def _init_app(self):
        """
        Initializes the web application.
        """
        app = web.Application()
        app.on_shutdown.append(self._shutdown_app)
        aiohttp_jinja2.setup(
            app, loader=jinja2.PackageLoader('src', 'templates'))
        app.router.add_get('/', self.index)
        app.router.add_post('/music/play/', self.play_music)
        app.router.add_post('/music/stop/', self.stop_music)
        app.router.add_post('/music/volume/', self.set_music_volume)
        app.router.add_post('/sound/play/', self.play_sound)
        app.router.add_post('/sound/volume/', self.set_sound_volume)
        app.router.add_static('/static/',
                              path=PROJECT_ROOT / 'static',
                              name='static')
        return app

    async def _shutdown_app(self, app):
        """
        Called when the app shut downs. Perform clean-up.
        """
        pass

    async def index(self, request):
        """
        Handles the client connection.
        """
        context = {
            "music": {
                "volume": self.music.volume,
                "currently_playing": self.music.currently_playing,
                "track_lists": self.music.track_lists
            },
            "sound": {
                "volume": self.sound.volume,
                "groups": self.sound.groups
            }
        }
        return aiohttp_jinja2.render_template('index.html', request, context)

    async def play_music(self, request):
        post_dict = await request.post()
        if "index" in post_dict:
            index = int(post_dict["index"])
            await self.music.play_track_list(index)
            return Response(status=200)
        return Response(status=400)

    async def stop_music(self, request):
        self.music.cancel()
        return Response(status=200)

    async def set_music_volume(self, request):
        post_dict = await request.post()
        if "volume" in post_dict:
            volume = float(post_dict["volume"])
            self.music.set_volume(volume)
            return Response(status=200)
        return Response(status=400)

    async def play_sound(self, request):
        post_dict = await request.post()
        if "groupIndex" in post_dict and "soundIndex" in post_dict:
            group_index = int(post_dict["groupIndex"])
            sound_index = int(post_dict["soundIndex"])
            await self.sound.play_sound(group_index, sound_index)
            return Response(status=200)
        return Response(status=400)

    async def set_sound_volume(self, request):
        post_dict = await request.post()
        if "volume" in post_dict:
            volume = float(post_dict["volume"])
            self.sound.set_volume(volume)
            return Response(status=200)
        return Response(status=400)
