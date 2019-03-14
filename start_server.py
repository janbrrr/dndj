import asyncio

from src.server import MusicManager

if __name__ == "__main__":
    manager = MusicManager("config.json")
    asyncio.run(manager.start_server())
