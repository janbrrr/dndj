import asyncio

from src.server import SoundServer

if __name__ == "__main__":
    server = SoundServer("config.json")
    asyncio.run(server.start_server())
