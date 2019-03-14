import asyncio
import json
import random
import logging

import pygame.mixer as mixer

from src.sounds import Sound
from src.music import MusicManager

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


class SoundServer:
    STATE_SCENE_SELECTION = 0
    STATE_SOUND_SELECTION = 1

    SLEEP_TIME = 0.01

    def __init__(self, config_path):
        mixer.init()
        with open(config_path) as config_file:
            config = json.load(config_file)
        self.music = MusicManager(config["music"], mixer.music)
        self.sounds = tuple(Sound.from_dict(config["sound"]["sounds"]))

    async def handle_connection(self, reader, writer):
        """
        Handles the client connection.
        """
        state = self.STATE_SCENE_SELECTION

        while True:
            if state == self.STATE_SCENE_SELECTION:
                state = await self._handle_scene_selection(reader, writer)
            elif state == self.STATE_SOUND_SELECTION:
                state = await self._handle_sound_selection(reader, writer)

    async def _handle_scene_selection(self, reader, writer) -> int:
        """
        Handles the scene selection with the client.
        Returns the new state.
        """
        writer.write(self._get_scene_selection_message().encode())
        await writer.drain()

        data = await reader.read(1000)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        logging.debug(f"Received {message!r} from {addr!r}")

        index = int(message) - 1
        if index in range(0, len(self.music.track_lists)):
            self.music.play_track_list(index)
            writer.write(f"Now playing: {self.music.track_lists[index].name}\n\n".encode())
            return self.STATE_SCENE_SELECTION
        elif index == -1:
            return self.STATE_SOUND_SELECTION
        else:
            logging.error(f"Received invalid index ({index}). Closing the connection.")
            writer.close()
            return self.STATE_SCENE_SELECTION

    def _get_scene_selection_message(self) -> str:
        """
        Returns a message listing the available track list options as `(<index>) <name>`.
        The first option is to switch to the sound menu.
        """
        message = "Available Scenes\n(0) Switch to Sounds\n"
        for index, track_list in enumerate(self.music.track_lists):
            message += f"({index+1}) {track_list.name}\n"
        return message

    async def _handle_sound_selection(self, reader, writer) -> int:
        """
        Handles the sound selection with the client.
        Returns the new state.
        """
        writer.write(self._get_sound_selection_message().encode())
        await writer.drain()

        data = await reader.read(1000)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        logging.debug(f"Received {message!r} from {addr!r}")

        index = int(message) - 1
        if index in range(0, len(self.sounds)):
            self._schedule_sound(index)
            writer.write(f"Now playing: {self.sounds[index].name}\n\n".encode())
            return self.STATE_SOUND_SELECTION
        elif index == -1:  # Switch to scenes
            return self.STATE_SCENE_SELECTION
        else:
            logging.error(f"Received invalid index ({index}). Closing the connection.")
            writer.close()
            return self.STATE_SOUND_SELECTION

    def _get_sound_selection_message(self):
        """
        Returns a message listing the available sound options as `(<index>) <name>`.
        The first option is to switch back to the scene menu.
        """
        message = "Available Sound Options\n(0) Switch to Scenes\n"
        for index, sound in enumerate(self.sounds):
            message += f"({index + 1}) {sound.name}\n"
        return message

    def _schedule_sound(self, index):
        """
        Creates an asynchronous task to play the sound at the given index.
        """
        sound = self.sounds[index]
        loop = asyncio.get_event_loop()
        play_sound_task = loop.create_task(self._play_sound(sound))

    async def start_server(self):
        """
        Starts the server.
        """
        server = await asyncio.start_server(
            self.handle_connection, '127.0.0.1', 8888)

        addr = server.sockets[0].getsockname()
        logging.info(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    async def _play_sound(self, sound: Sound):
        """
        Plays the given sound.
        """
        await self.music.set_volume(0.3)
        logging.debug(f"Loading '{sound.name}'")
        file = random.choice(sound.files)
        sound = mixer.Sound(file)
        sound.play()
        logging.info(f"Now Playing: {file}")
        await asyncio.sleep(sound.get_length())
        logging.info(f"Finished playing: {file}")
        await self.music.set_volume(1)
