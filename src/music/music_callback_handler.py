from typing import Callable, Optional

from aiohttp.web_request import Request

from src.music.music_actions import MusicActions
from src.music.music_callback_info import MusicCallbackInfo


class MusicCallbackHandler:
    def __init__(self, callback_fn: Callable = None):
        self.callback_fn = callback_fn

    async def __call__(self, action: MusicActions, request: Request, music_info: Optional[MusicCallbackInfo]):
        if self.callback_fn is not None:
            await self.callback_fn(action=action, request=request, music_info=music_info)