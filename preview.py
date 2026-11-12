#!/usr/bin/env python3
"""Build and serve the local site, printing the exact preview URL."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from subprocess import run
import sys


ROOT = Path(__file__).resolve().parent
run([sys.executable, str(ROOT / "build.py"), "--check"], cwd=ROOT, check=True)

# Port 0 asks the OS for a free port, avoiding conflicts with other local servers.

class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "dist"), **kwargs)

    def send_error(self, code, message=None, explain=None):
        if code != 404:
            return super().send_error(code, message, explain)
        language = "zh/" if self.path.startswith("/zh/") else ""
        page = (ROOT / "dist" / language / "404.html").read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(page)


handler = PreviewHandler
server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
url = f"http://127.0.0.1:{server.server_port}/"
print(f"\nOpen this exact address in your browser: {url}", flush=True)
print("Press Ctrl-C here when finished. Do not add /dist/ to the address.\n", flush=True)

try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
