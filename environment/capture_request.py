"""Local request recorder used only to verify isolation.

Listens on 127.0.0.1, writes the JSON body of each POST it receives to a file
(headers are never stored, so no credential is written), and answers with an
error so nothing is forwarded anywhere. Point the CLI at it with
ANTHROPIC_BASE_URL=http://127.0.0.1:<port> to see exactly what the CLI would
send to the model.

Usage: python3 capture_request.py <port> <out_dir>
"""
import http.server
import os
import sys

PORT, OUT = int(sys.argv[1]), sys.argv[2]
count = 0


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global count
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        count += 1
        name = "%02d_%s.json" % (count, self.path.strip("/").replace("/", "_").split("?")[0])
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(body)
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"type":"error","error":{"type":"invalid_request_error","message":"capture only"}}')

    do_GET = do_POST

    def log_message(self, *a):
        pass


os.makedirs(OUT, exist_ok=True)
http.server.HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
