"""Local request recorder used only to verify isolation.

Listens on 127.0.0.1, writes the JSON body of each POST it receives to a file
(headers are never stored, so no credential is written), and answers with an
error so nothing is forwarded anywhere. Point the CLI at it with
ANTHROPIC_BASE_URL=http://127.0.0.1:<port> to see exactly what the CLI would
send to the model.

With a third argument "reply" it answers /v1/messages with a fixed fake
assistant message ("CANNED ASSISTANT REPLY n") instead of an error, so a
multi-turn conversation can continue and the later requests can be recorded.

Usage: python3 capture_request.py <port> <out_dir> [reply]
"""
import http.server
import os
import sys

import json

PORT, OUT = int(sys.argv[1]), sys.argv[2]
REPLY = len(sys.argv) > 3 and sys.argv[3] == "reply"
count = 0


def canned_sse(n):
    text = "CANNED ASSISTANT REPLY %d" % n
    events = [
        ("message_start", {"type": "message_start", "message": {
            "id": "msg_canned%d" % n, "type": "message", "role": "assistant", "model": "canned",
            "content": [], "stop_reason": None, "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 1}}}),
        ("content_block_start", {"type": "content_block_start", "index": 0,
                                 "content_block": {"type": "text", "text": ""}}),
        ("content_block_delta", {"type": "content_block_delta", "index": 0,
                                 "delta": {"type": "text_delta", "text": text}}),
        ("content_block_stop", {"type": "content_block_stop", "index": 0}),
        ("message_delta", {"type": "message_delta",
                           "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                           "usage": {"output_tokens": 5}}),
        ("message_stop", {"type": "message_stop"}),
    ]
    return "".join("event: %s\ndata: %s\n\n" % (e, json.dumps(d)) for e, d in events).encode()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global count
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        count += 1
        name = "%02d_%s.json" % (count, self.path.strip("/").replace("/", "_").split("?")[0])
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(body)
        if REPLY and self.path.startswith("/v1/messages") and "count_tokens" not in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            self.wfile.write(canned_sse(count))
            return
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"type":"error","error":{"type":"invalid_request_error","message":"capture only"}}')

    do_GET = do_POST

    def log_message(self, *a):
        pass


os.makedirs(OUT, exist_ok=True)
http.server.HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
