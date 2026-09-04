import os
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"celery worker alive")

    def log_message(self, format, *args):
        pass


def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0",port), HealthCheckHandler)
    server.serve_forever()


if __name__ == "__main__":
    # Health server runs in a background thread just to satisfy Pxxl's
    # proxy route check. It does nothing real - the Celery worker below
    # is the actual process.
    threading.Thread(target=run_health_server, daemon=True).start()

    subprocess.run([
        "celery",
        "-A", "app.core.celery_app.celery_app",
        "worker",
        "--loglevel=info",
    ])