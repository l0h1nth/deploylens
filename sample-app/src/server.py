from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/healthz":
            self.send_json({"status": "ok"})
            return

        self.send_json(
            {
                "service": "deploylens-sample",
                "message": "This sample app exists so DeployLens can analyze a real deployment.",
            }
        )

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_json(self, payload: dict[str, str]) -> None:
        body = dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
