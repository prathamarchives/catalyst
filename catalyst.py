"""catalyst.py — launch the local Catalyst app.

Starts the local server and opens your browser to the UI. One command:

    py catalyst.py        (or double-click run.cmd on Windows / ./run.sh on macOS/Linux)

Local-first: binds 127.0.0.1, no account, no cloud. Ctrl+C to stop.
"""
from __future__ import annotations

import importlib.util
import threading
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE / "apps" / "control-panel" / "server.py"


def _load_server():
    spec = importlib.util.spec_from_file_location("catalyst_server", SERVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    server = _load_server()
    url = f"http://{server.HOST}:{server.PORT}"
    # open the browser shortly after the server starts serving
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"Catalyst -> {url} (opening your browser…)")
    return server.main()


if __name__ == "__main__":
    raise SystemExit(main())
