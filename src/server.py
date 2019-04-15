import uuid

import aiohttp
import json
import yaml
import logging
import pathlib

import jinja2

import aiohttp_jinja2
from aiohttp import web

from src.loader import CustomLoader
from src.music import MusicManager
from src.sounds import SoundManager

logging.basicConfig(format='%(levelname)-6s: %(message)s', level=logging.DEBUG)

PROJECT_ROOT = pathlib.Path(__file__).parent


class Server:

    def __init__(self, config_path, host, port):
        with open(config_path) as config_file:
            config = yaml.load(config_file, Loader=CustomLoader)
        self.music = MusicManager(config["music"])
        self.sound = SoundManager(config["sound"])
        self.app = None
        self.host = host
        self.port = port

    def start(self):
        """
        Starts the web server.
        """
        self.app = self._init_app()
        logging.info(f'Server started on http://{self.host}:{self.port}')
        web.run_app(self.app, host=self.host, port=self.port)

    async def _init_app(self):
        """
        Initializes the web application.
        """
        app = web.Application()
        app['websockets'] = {}
        app.on_shutdown.append(self._shutdown_app)
        aiohttp_jinja2.setup(
            app, loader=jinja2.PackageLoader('src', 'templates'))
        app.router.add_get('/', self.index)
        app.router.add_static('/static/',
                              path=PROJECT_ROOT / 'static',
                              name='static')
        return app

    async def _shutdown_app(self, app):
        """
        Called when the app shut downs. Perform clean-up.
        """
        for ws in app['websockets'].values():
            await ws.close()
        app['websockets'].clear()

    def _get_page(self, request):
        """
        Returns the index page.
        """
        context = {
            "music": {
                "volume": self.music.volume,
                "currently_playing": self.music.currently_playing,
                "groups": self.music.groups
            },
            "sound": {
                "volume": self.sound.volume,
                "groups": self.sound.groups
            }
        }
        return aiohttp_jinja2.render_template('index.html', request, context)

    async def index(self, request):
        """
        Handles the client connection.
        """
        ws_current = web.WebSocketResponse()
        ws_ready = ws_current.can_prepare(request)
        if not ws_ready.ok:
            return self._get_page(request)
        await ws_current.prepare(request)

        ws_identifier = str(uuid.uuid4())
        request.app['websockets'][ws_identifier] = ws_current
        logging.info(f"Client {ws_identifier} connected.")
        try:
            while True:
                msg = await ws_current.receive()
                if msg.type == aiohttp.WSMsgType.text:
                    data_dict = json.loads(msg.data)
                    if "action" in data_dict:
                        if data_dict["action"] == "playMusic":
                            if "groupIndex" in data_dict and "trackListIndex" in data_dict:
                                group_index = int(data_dict["groupIndex"])
                                track_list_index = int(data_dict["trackListIndex"])
                                await self._play_music(request, group_index, track_list_index)
                        elif data_dict["action"] == "stopMusic":
                            await self._stop_music(request)
                        elif data_dict["action"] == "setMusicVolume":
                            if "volume" in data_dict:
                                volume = float(data_dict["volume"])
                                await self._set_music_volume(request, volume)
                        elif data_dict["action"] == "playSound":
                            if "groupIndex" in data_dict and "soundIndex" in data_dict:
                                group_index = int(data_dict["groupIndex"])
                                sound_index = int(data_dict["soundIndex"])
                                await self._play_sound(group_index, sound_index)
                        elif data_dict["action"] == "setSoundVolume":
                            if "volume" in data_dict:
                                volume = float(data_dict["volume"])
                                await self._set_sound_volume(request, volume)
        except RuntimeError:
            logging.info(f"Client {ws_identifier} disconnected.")
            del request.app["websockets"][ws_identifier]
            return ws_current

    async def _play_music(self, request, group_index, track_list_index):
        """
        Starts to play the music and notifies all connected web sockets.
        """
        group = self.music.groups[group_index]
        group_name = group.name
        track_name = group.track_lists[track_list_index].name
        await self.music.play_track_list(group_index, track_list_index)
        for ws in request.app["websockets"].values():
            await ws.send_json(
                    {"action": "nowPlaying", "groupIndex": group_index,
                     "trackListIndex": track_list_index,
                     "groupName": group_name, "trackName": track_name})

    async def _stop_music(self, request):
        """
        Stops the music and notifies all connected web sockets.
        """
        await self.music.cancel()
        for ws in request.app["websockets"].values():
            await ws.send_json({"action": "musicStopped"})

    async def _set_music_volume(self, request, volume):
        """
        Sets the music volume and notifies all connected web sockets.
        """
        await self.music.set_volume(volume, seconds=1)
        for ws in request.app["websockets"].values():
            await ws.send_json({"action": "setMusicVolume", "volume": volume})

    async def _play_sound(self, group_index, sound_index):
        """
        Plays the sound.
        """
        await self.sound.play_sound(group_index, sound_index)

    async def _set_sound_volume(self, request, volume):
        """
        Sets the sound volume and notifies all connected web sockets.
        """
        self.sound.set_volume(volume)
        for ws in request.app["websockets"].values():
            await ws.send_json({"action": "setSoundVolume", "volume": volume})
