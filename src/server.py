import asyncio
import json
import random
import logging

import pygame.mixer as mixer

from src.sounds import Sound
from src.tracks import TrackList


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


class MusicManager:
    STATE_SCENE_SELECTION = 0
    STATE_SOUND_SELECTION = 1

    SLEEP_TIME = 0.01

    def __init__(self, config_path):
        mixer.init()
        with open(config_path) as config_file:
            config = json.load(config_file)
        self.track_lists = tuple(TrackList.from_dict(config["scenes"]))
        self.track_currently_playing = None
        self.sounds = tuple(Sound.from_dict(config["sounds"]))
        self.is_playing_sound = False

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
        if index in range(0, len(self.track_lists)):
            self._schedule_track(index)
            writer.write(f"Now playing: {self.track_lists[index].name}\n\n".encode())
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
        for index, track_list in enumerate(self.track_lists):
            message += f"({index+1}) {track_list.name}\n"
        return message

    def _schedule_track(self, index):
        """
        Creates an asynchronous task to play the track at the given index.
        If a track is already being played as indicated by `self.track_currently_playing`, it will be cancelled
        and the new track will be played.
        """
        track_list = self.track_lists[index]
        if self.track_currently_playing is not None:
            self.track_currently_playing.cancel()
        loop = asyncio.get_event_loop()
        self.track_currently_playing = loop.create_task(self._play_track_list(track_list))

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

    async def _play_track_list(self, track_list: TrackList):
        """
        Plays the given track list.

        When a sound is being played, the volume of the track list will be lowered and increased again after the
        sound finishes playing.
        """
        logging.debug(f"Loading '{track_list.name}'")
        while True:
            tracks = list(track_list.tracks)  # Copy since random will shuffle in place
            if track_list.shuffle:
                random.shuffle(tracks)
            for track in tracks:
                mixer.music.load(track.file_path)
                mixer.music.play()
                if track.start_at is not None:
                    mixer.music.set_pos(track.start_at)
                logging.info(f"Now Playing: {track.file_path}")
                has_lowered_volume = False
                while mixer.music.get_busy():
                    if self.is_playing_sound and not has_lowered_volume:
                        mixer.music.set_volume(0.5)
                        has_lowered_volume = True
                        logging.debug(f"Lowered volume {track.file_path}")
                    elif not self.is_playing_sound and has_lowered_volume:
                        mixer.music.set_volume(1)
                        has_lowered_volume = False
                        logging.debug(f"Increased volume {track.file_path}")
                    try:
                        await asyncio.sleep(self.SLEEP_TIME)
                    except asyncio.CancelledError:
                        mixer.music.stop()
                        self.track_currently_playing = None
                        logging.info(f"Stopped {track.file_path}")
                        raise
                logging.info(f"Finished playing: {track.file_path}")
            if not track_list.loop:
                break

    async def _play_sound(self, sound: Sound):
        """
        Plays the given sound.
        First, `self.is_playing_sound` is set to indicate that a sound is going to be played.
        Then the control is given to the event loop that will give control to the track that is being played
        and this track will lower its volume.
        After playing the sound `self.is_playing_sound` is unset to signal the track to resume playing.
        """
        self.is_playing_sound = True
        await asyncio.sleep(self.SLEEP_TIME)  # Back to the track list task, it will lower its volume
        logging.debug(f"\tLoading '{sound.name}'")
        file = random.choice(sound.files)
        sound = mixer.Sound(file)
        sound.play()
        logging.info(f"Now Playing: {file}")
        await asyncio.sleep(sound.get_length())
        logging.info(f"Finished playing: {file}")
        self.is_playing_sound = False
