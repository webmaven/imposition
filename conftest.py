import sys
from unittest.mock import MagicMock

# Mock browser-specific modules before any other imports
sys.modules['js'] = MagicMock()
sys.modules['pyodide'] = MagicMock()
sys.modules['pyodide.ffi'] = MagicMock()

import pytest
import http.server
import socketserver
import threading
import os

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve files out of the epub_py directory
        # With pytest running from the `imposition` directory,
        # the server should serve files from its CWD.
        super().__init__(*args, **kwargs)

@pytest.fixture(scope="session")
def http_server(request):
    """
    pytest fixture for a simple HTTP server.
    """
    # Allow the port to be reused
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    def teardown():
        httpd.shutdown()
        httpd.server_close()

    request.addfinalizer(teardown)

    return f"http://localhost:{PORT}/index.html"
