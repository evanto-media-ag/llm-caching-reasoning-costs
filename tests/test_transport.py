import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from lab import transport


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", 0))
        self.rfile.read(length)
        if self.path == "/limit":
            self.send_response(429)
            self.send_header("retry-after", "3")
        else:
            self.send_response(200)
            self.send_header("set-cookie", "a=b")
            self.send_header("x-request-id", "req-1")
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"path": self.path}).encode())

    def log_message(self, *args):
        pass


class TransportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_send_returns_error_response(self):
        r = transport.send("POST", self.base + "/limit", {}, {"a": 1})
        self.assertEqual(r.status, 429)
        self.assertEqual(r.headers["retry-after"], "3")

    def test_send_filters_headers(self):
        r = transport.send("POST", self.base + "/ok", {}, {"a": 1})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, {"path": "/ok"})
        self.assertEqual(r.headers, {"x-request-id": "req-1"})


if __name__ == "__main__":
    unittest.main()
