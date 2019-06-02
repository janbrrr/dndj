import asyncio
import collections
import functools
import logging
from typing import Dict, List


ActiveSound = collections.namedtuple("ActiveSound", ["group_index", "sound_index", "task"])


class SoundTracker:
    """
    This class tracks the `asyncio.Task` instances for playing sounds.
    """

    def __init__(self):
        self.sound_to_task: Dict[str, asyncio.Task] = {}

    def _get_sound_key(self, group_index: int, sound_index: int):
        """
        Returns the key for the `self.sound_to_task` dictionary.
        """
        return f"{group_index}-{sound_index}"

    @property
    def active_sounds(self) -> List[ActiveSound]:
        """
        Returns a list of the sounds that are currently being played.
        """
        active_sounds = []
        for key in self.sound_to_task.keys():
            group_index = int(key.split("-")[0])
            sound_index = int(key.split("-")[1])
            task = self.sound_to_task[key]
            active_sounds.append(ActiveSound(group_index, sound_index, task))
        return active_sounds

    def register_sound(self, group_index: int, sound_index: int, task: asyncio.Task):
        """
        Register that the given task belongs to the given group_index and sound_index. Will automatically
        unregister the task after it has finished.

        Raises a `RuntimeError` if the task is already done. Finished tasks are not allowed to be registered.
        """
        logging.debug(f"Registering task for group={group_index}, sound={sound_index}")
        key = self._get_sound_key(group_index, sound_index)
        if task.done():
            raise RuntimeError(f"Task for group={group_index}, sound={sound_index} is done, but was registered!")
        task.add_done_callback(functools.partial(self._unregister_sound, group_index, sound_index))
        self.sound_to_task[key] = task

    def _unregister_sound(self, group_index: int, sound_index: int, _):
        """
        Unregister the task that belongs to the given group_index and sound_index.

        Raises a `RuntimeError` if the task is already done. Finished tasks are not allowed to be registered.
        """
        logging.debug(f"Unregistering task for group={group_index}, sound={sound_index}")
        key = self._get_sound_key(group_index, sound_index)
        task = self.sound_to_task[key]
        if not task.done():
            raise RuntimeError(f"Task for group={group_index}, sound={sound_index} is not done, but was unregistered!")
        del self.sound_to_task[key]

    async def cancel_sound(self, group_index: int, sound_index: int):
        """
        Cancels a task that has previously been registered for the given sound. Does nothing if there is no such task.
        """
        logging.debug(f"Cancelling task for group={group_index}, sound={sound_index}")
        key = self._get_sound_key(group_index, sound_index)
        if key not in self.sound_to_task:
            return
        task = self.sound_to_task[key]
        task.cancel()
        while not task.done():
            await asyncio.sleep(0.01)
