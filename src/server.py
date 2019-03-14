import asyncio
import json
import random
import logging

import vlc

from src.sounds import Sound
from src.tracks import TrackList


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


class MusicManager:
    STATE_SCENE_SELECTION = 0
    STATE_SOUND_SELECTION = 1

    SLEEP_TIME = 0.01

    def __init__(self, config_path):
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
        logging.debug(f"Loading '{track_list.name}'")
        while True:
            tracks = list(track_list.tracks)  # Copy since random will shuffle in place
            if track_list.shuffle:
                random.shuffle(tracks)
            for track in tracks:
                player = vlc.MediaPlayer(vlc.Instance(), f"file:///{track.file_path}")
                success = player.play()
                if success == -1:
                    raise RuntimeError(f"Failed to play {track.file_path}")
                if track.start_at is not None:
                    player.set_time(track.start_at)
                logging.info(f"Now Playing: {track.file_path}")
                await asyncio.sleep(2)  # Give the media player time to start the song
                while player.is_playing() or player.get_state() == vlc.State.Paused:
                    current_state = player.get_state()
                    if self.is_playing_sound and not current_state == vlc.State.Paused:
                        player.set_pause(1)
                        logging.info(f"Paused {track.file_path}")
                    elif not self.is_playing_sound and current_state == vlc.State.Paused:
                        player.set_pause(0)
                        logging.info(f"Resumed {track.file_path}")
                    time = player.get_time()
                    duration = player.get_length()
                    remaining_time_in_ms = duration - time
                    try:
                        await asyncio.sleep(self.SLEEP_TIME)
                    except asyncio.CancelledError:
                        player.stop()
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
        and this track will mute itself.
        After playing the sound `self.is_playing_sound` is unset to signal the track to resume playing.
        """
        self.is_playing_sound = True
        await asyncio.sleep(self.SLEEP_TIME)  # Back to the track list task, it will pause
        logging.debug(f"\tLoading '{sound.name}'")
        file = random.choice(sound.files)
        player = vlc.MediaPlayer(vlc.Instance(), f"file:///{file}")
        success = player.play()
        if success == -1:
            raise RuntimeError(f"Failed to play {file}")
        logging.info(f"Now Playing: {file}")
        await asyncio.sleep(0.5)  # Give the media player time to start the song
        while player.is_playing():
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                player.stop()
                logging.info(f"Stopped {file}")
                raise
        logging.info(f"Finished playing: {file}")
        self.is_playing_sound = False
