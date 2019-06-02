import asyncio
import pytest

from src.sound.sound_tracker import SoundTracker


class TestSoundTracker:

    def test_get_sound_key(self):
        tracker = SoundTracker()
        assert tracker._get_sound_key(0, 0) == "0-0"
        assert tracker._get_sound_key(1, 0) == "1-0"
        assert tracker._get_sound_key(0, 1) == "0-1"

    async def test_register_sound(self, loop):
        tracker = SoundTracker()
        task = loop.create_task(asyncio.sleep(0.001))
        tracker.register_sound(0, 1, task)
        assert tracker.sound_to_task[tracker._get_sound_key(0, 1)] == task

    async def test_register_sound_raises_if_task_done(self, loop):
        tracker = SoundTracker()
        task = loop.create_task(asyncio.sleep(0.001))
        await task
        with pytest.raises(RuntimeError):
            tracker.register_sound(0, 0, task)

    async def test_automatically_unregisters_sound_if_done(self, loop):
        tracker = SoundTracker()
        task = loop.create_task(asyncio.sleep(0.001))
        tracker.register_sound(0, 1, task)
        key = tracker._get_sound_key(0, 1)
        assert tracker.sound_to_task[tracker._get_sound_key(0, 1)] == task
        await task
        assert key not in tracker.sound_to_task

    async def test_unregister_sound_raises_if_task_not_done(self, loop):
        tracker = SoundTracker()
        task = loop.create_task(asyncio.sleep(0.001))
        tracker.register_sound(0, 1, task)
        with pytest.raises(RuntimeError):
            tracker._unregister_sound(0, 1, None)

    async def test_cancel_sound_cancels_task(self, loop):
        tracker = SoundTracker()
        task = loop.create_task(asyncio.sleep(0.001))
        key = tracker._get_sound_key(0, 1)
        tracker.register_sound(0, 1, task)
        assert key in tracker.sound_to_task
        await tracker.cancel_sound(0, 1)
        assert task.cancelled()
        assert key not in tracker.sound_to_task

    async def test_active_sounds(self, loop):
        tracker = SoundTracker()
        assert len(tracker.active_sounds) == 0
        task = loop.create_task(asyncio.sleep(0.001))
        tracker.register_sound(0, 1, task)
        assert len(tracker.active_sounds) == 1
        assert tracker.active_sounds[0]
