import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

def _run_server():
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), _Handler)
    server.serve_forever()

def keep_alive():
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()
