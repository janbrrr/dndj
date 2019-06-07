import json
import logging
import pathlib
import uuid
from typing import Optional

import aiohttp
import aiohttp_jinja2
import jinja2
import yaml
from aiohttp import web
from aiohttp.web_request import Request

from src.loader import CustomLoader
from src.music import MusicActions, MusicCallbackInfo, MusicManager
from src.sound import SoundActions, SoundCallbackInfo, SoundManager


logging.basicConfig(
    format="%(asctime)s | %(levelname)-6s | %(name)-25s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = pathlib.Path(__file__).parent


class Server:
    def __init__(self, config_path, host, port):
        with open(config_path) as config_file:
            config = yaml.load(config_file, Loader=CustomLoader)
        self.music = MusicManager(config["music"], callback_fn=self.on_music_changes)
        self.sound = SoundManager(config["sound"], callback_fn=self.on_sound_changes)
        self.app = None
        self.host = host
        self.port = port

    def start(self):
        """
        Starts the web server.
        """
        self.app = self._init_app()
        logger.info(f"Server started on http://{self.host}:{self.port}")
        web.run_app(self.app, host=self.host, port=self.port)

    async def _init_app(self):
        """
        Initializes the web application.
        """
        app = web.Application()
        app["websockets"] = {}
        app.on_shutdown.append(self._shutdown_app)
        aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader("src", "templates"))
        app.router.add_get("/", self.index)
        app.router.add_static("/static/", path=PROJECT_ROOT / "static", name="static")
        return app

    async def _shutdown_app(self, app):
        """
        Called when the app shut downs. Perform clean-up.
        """
        for ws in app["websockets"].values():
            await ws.close()
        app["websockets"].clear()

    def _get_page(self, request):
        """
        Returns the index page.
        """
        context = {
            "music": {
                "volume": self.music.volume,
                "currently_playing": self.music.currently_playing,
                "groups": self.music.groups,
            },
            "sound": {
                "volume": self.sound.volume,
                "groups": self.sound.groups,
                "groups_currently_playing": [sound_info.group_index for sound_info in self.sound.currently_playing],
                "sounds_currently_playing": [
                    (sound_info.group_index, sound_info.sound_index) for sound_info in self.sound.currently_playing
                ],
            },
        }
        return aiohttp_jinja2.render_template("index.html", request, context)

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
        request.app["websockets"][ws_identifier] = ws_current
        logger.info(f"Client {ws_identifier} connected.")
        try:
            while True:
                msg = await ws_current.receive()
                await self._handle_message(request, msg)
        except RuntimeError:
            logger.info(f"Client {ws_identifier} disconnected.")
            del request.app["websockets"][ws_identifier]
            return ws_current

    async def _handle_message(self, request, msg):
        if msg.type != aiohttp.WSMsgType.text:
            return
        data_dict = json.loads(msg.data)
        if "action" not in data_dict:
            return
        action = data_dict["action"]
        if action == "playMusic":
            if "groupIndex" in data_dict and "trackListIndex" in data_dict:
                group_index = int(data_dict["groupIndex"])
                track_list_index = int(data_dict["trackListIndex"])
                await self._play_music(request, group_index, track_list_index)
        elif action == "stopMusic":
            await self._stop_music(request)
        elif action == "setMusicVolume":
            if "volume" in data_dict:
                volume = float(data_dict["volume"])
                await self._set_music_volume(request, volume)
        elif action == "playSound":
            if "groupIndex" in data_dict and "soundIndex" in data_dict:
                group_index = int(data_dict["groupIndex"])
                sound_index = int(data_dict["soundIndex"])
                await self._play_sound(request, group_index, sound_index)
        elif action == "stopSound":
            if "groupIndex" in data_dict and "soundIndex" in data_dict:
                group_index = int(data_dict["groupIndex"])
                sound_index = int(data_dict["soundIndex"])
                await self._stop_sound(group_index, sound_index)
        elif action == "setSoundVolume":
            if "volume" in data_dict:
                volume = float(data_dict["volume"])
                await self._set_sound_volume(request, volume)

    async def _play_music(self, request, group_index, track_list_index):
        """
        Starts to play the music and notifies all connected web sockets.
        """
        await self.music.play_track_list(request, group_index, track_list_index)

    async def _stop_music(self, request):
        """
        Stops the music and notifies all connected web sockets.
        """
        await self.music.cancel(request)

    async def _set_music_volume(self, request, volume):
        """
        Sets the music volume and notifies all connected web sockets.
        """
        await self.music.set_volume(volume, seconds=1)
        for ws in request.app["websockets"].values():
            await ws.send_json({"action": "setMusicVolume", "volume": volume})

    async def _play_sound(self, request, group_index, sound_index):
        """
        Plays the sound.
        """
        await self.sound.play_sound(request, group_index, sound_index)

    async def _stop_sound(self, group_index, sound_index):
        """
        Stops the sound.
        """
        await self.sound.cancel_sound(group_index, sound_index)

    async def _set_sound_volume(self, request, volume):
        """
        Sets the sound volume and notifies all connected web sockets.
        """
        self.sound.set_volume(volume)
        for ws in request.app["websockets"].values():
            await ws.send_json({"action": "setSoundVolume", "volume": volume})

    async def on_music_changes(self, action: MusicActions, request: Request, music_info: Optional[MusicCallbackInfo]):
        """
        Callback function used by the `MusicManager` at `self.music`.

        Notifies all connected web sockets about the changes.
        """
        if action == MusicActions.START:
            logger.debug(f"Music Callback: Start")
            for ws in request.app["websockets"].values():
                await ws.send_json(
                    {
                        "action": "nowPlaying",
                        "groupIndex": music_info.group_index,
                        "trackListIndex": music_info.track_list_index,
                        "groupName": music_info.group_name,
                        "trackName": music_info.track_list_name,
                    }
                )
        elif action == MusicActions.STOP:
            logger.debug(f"Music Callback: Stop")
            for ws in request.app["websockets"].values():
                await ws.send_json({"action": "musicStopped"})
        elif action == MusicActions.FINISH:
            logger.debug(f"Music Callback: Finish")
            for ws in request.app["websockets"].values():
                await ws.send_json({"action": "musicFinished"})

    async def on_sound_changes(self, action: SoundActions, request: Request, sound_info: Optional[SoundCallbackInfo]):
        """
        Callback function used by the `SoundManager` at `self.sound`.

        Notifies all connected web sockets about the changes.
        """
        sound_info_dict = {
            "groupIndex": sound_info.group_index,
            "soundIndex": sound_info.sound_index,
            "groupName": sound_info.group_name,
            "soundName": sound_info.sound_name,
        }
        if action == SoundActions.START:
            logger.debug(f"Sound Callback: Start")
            for ws in request.app["websockets"].values():
                await ws.send_json({"action": "soundPlaying", **sound_info_dict})
        elif action == SoundActions.STOP:
            logger.debug(f"Music Callback: Stop")
            for ws in request.app["websockets"].values():
                await ws.send_json({"action": "soundStopped", **sound_info_dict})
        elif action == SoundActions.FINISH:
            logger.debug(f"Music Callback: Finish")
            for ws in request.app["websockets"].values():
                await ws.send_json({"action": "soundFinished", **sound_info_dict})
