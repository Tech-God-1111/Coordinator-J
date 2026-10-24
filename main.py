
"""
Coordinator-J
Local web interface launcher.

This milestone serves the existing frontend files.
The Python coordinator is not connected to the browser UI yet.
"""

import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from functools import partial


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

HOST = "127.0.0.1"
PORT = 8000


class CoordinatorRequestHandler(SimpleHTTPRequestHandler):
    """Serve the Coordinator-J frontend from the frontend directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_GET(self):
        # Open the welcome page when visiting the root URL.
        if self.path == "/":
            self.path = "/Index.html"

        super().do_GET()

    def log_message(self, format_string, *args):
        """Keep useful request logs in the terminal."""
        print(f"[Coordinator-J] {self.address_string()} - "
              f"{format_string % args}")


def main():
    if not FRONTEND_DIR.is_dir():
        raise FileNotFoundError(
            f"Frontend directory not found: {FRONTEND_DIR}"
        )

    index_file = FRONTEND_DIR / "Index.html"
    dashboard_file = FRONTEND_DIR / "Dashboard.html"

    if not index_file.is_file():
        raise FileNotFoundError(
            f"Welcome page not found: {index_file}"
        )

    if not dashboard_file.is_file():
        raise FileNotFoundError(
            f"Dashboard page not found: {dashboard_file}"
        )

    server = ThreadingHTTPServer(
        (HOST, PORT),
        CoordinatorRequestHandler,
    )

    url = f"http://{HOST}:{PORT}/"

    print("=" * 46)
    print("             COORDINATOR-J")
    print("          Local Web Interface")
    print("=" * 46)
    print(f"Frontend: {FRONTEND_DIR}")
    print(f"Address:  {url}")
    print("Mode:     Frontend preview")
    print("Backend:  Not connected to the browser yet")
    print("\nPress Ctrl+C to stop Coordinator-J.")

    # Open the browser after the local server starts.
    threading.Timer(
        0.8,
        lambda: webbrowser.open(url),
    ).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCoordinator-J is shutting down.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
