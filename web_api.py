import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "backend"))

from coordinator import Coordinator

HOST = "127.0.0.1"
PORT = 8001
coordinator = Coordinator()


class APIHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:8000")
        self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        if self.path not in ("/api/command", "/api/health"):
            self.send_json(404, {"error": "Not found"})
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:8000")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self.send_json(200, {
                "ok": True,
                "service": "Coordinator-J API",
            })
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/command":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 10000:
                self.send_json(400, {"error": "Invalid request size"})
                return

            body = json.loads(self.rfile.read(length).decode("utf-8"))
            request = body.get("request") if isinstance(body, dict) else None

            if not isinstance(request, str) or not request.strip():
                self.send_json(400, {"error": "Request must be non-empty text"})
                return

            if len(request) > 500:
                self.send_json(400, {"error": "Request is too long"})
                return

            task, message = coordinator.handle_request(request.strip())
            self.send_json(200, {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
                "tool": task.selected_tool,
                "message": message,
            })

        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "Invalid JSON"})
        except Exception as exc:
            print(f"API error: {type(exc).__name__}")
            self.send_json(500, {"error": "Internal server error"})

    def log_message(self, format_string, *args):
        print("[Coordinator-J API] " + format_string % args)


def main():
    server = ThreadingHTTPServer((HOST, PORT), APIHandler)
    print(f"Coordinator-J API listening at http://{HOST}:{PORT}")
    print("Health check: http://127.0.0.1:8001/api/health")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCoordinator-J API stopping.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
