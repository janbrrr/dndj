import argparse

from src.check_version import check_youtube_dl_version
from src.server import Server


if __name__ == "__main__":
    """
    Starts the server with the provided YAML config file.

    Accepts the following optional arguments:
    --host "your.new.host.ip" (default="127.0.0.1")
    --port port_number (default=8080)

    Run this script as follows:
    `python start_server.py "path/to/config.yaml"`
    """
    parser = argparse.ArgumentParser(description="Start the server")
    parser.add_argument("config", metavar="C", help="path to the config file")
    parser.add_argument(
        "--host", dest="host", action="store", default="127.0.0.1", help="The host (default: 127.0.0.1)"
    )
    parser.add_argument("--port", dest="port", action="store", default=8080, help="The port (default: 8080)")

    args = parser.parse_args()
    check_youtube_dl_version()
    Server(config_path=args.config, host=args.host, port=args.port).start()
