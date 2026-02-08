import os
from http.server import BaseHTTPRequestHandler, HTTPServer

MESSAGE_FILE = os.getenv("MESSAGE_FILE", "/etc/config/message")
PORT = int(os.getenv("PORT", "8080"))


def read_message():
    try:
        with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() + "\n"
    except FileNotFoundError:
        return "message file not found\n"
    except Exception as error:
        return f"error reading message: {error}\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        message = read_message().encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(message)))
        self.end_headers()

        self.wfile.write(message)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()

