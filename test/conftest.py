import io
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


def make_zip_bytes(extracted_name: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(f"{extracted_name}/docs/readme.md", "# hello\n")
    return buf.getvalue()


def make_root_tree_zip_bytes(extracted_name: str) -> bytes:
    """A zip whose markdown lives at the repo root plus a subfolder,
    like OpenVoiceOS/architecture."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(f"{extracted_name}/README.md", "# root readme\n")
        zf.writestr(f"{extracted_name}/pipeline-1.md", "# pipeline spec\n")
        zf.writestr(f"{extracted_name}/appendix/foo.md", "# appendix foo\n")
        zf.writestr(f"{extracted_name}/LICENSE", "license text\n")
    return buf.getvalue()


class Handler(BaseHTTPRequestHandler):
    routes = {}

    def do_GET(self):
        body = self.routes.get(self.path)
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture
def http_server():
    Handler.routes = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]

    class Server:
        base_url = f"http://127.0.0.1:{port}"
        routes = Handler.routes

    yield Server
    server.shutdown()
    server.server_close()
