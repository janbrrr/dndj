from typing import Callable, Optional

from aiohttp.web_request import Request

from src.sound.sound_actions import SoundActions
from src.sound.sound_callback_info import SoundCallbackInfo


class SoundCallbackHandler:
    def __init__(self, callback_fn: Callable = None):
        self.callback_fn = callback_fn

    async def __call__(
        self, action: SoundActions, request: Request, sound_info: Optional[SoundCallbackInfo], master_volume: float
    ):
        if self.callback_fn is not None:
            await self.callback_fn(action=action, request=request, sound_info=sound_info, master_volume=master_volume)
