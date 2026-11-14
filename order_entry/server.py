"""Order-entry tool: a minimal MCP server (stdio, JSON-RPC, standard library only).

It offers one tool, enter_order. The tool does NOT judge safety: there are no
dose limits, alerts or hard stops. It checks only that the fields are present
and well-typed, appends the call to a ledger file, and returns a plain
acknowledgement. Rejected calls are appended to the ledger too, marked as
not accepted.

Usage: python3 server.py <ledger_path>
The ledger is a JSON-lines file, one line per call, written by this process.
"""
import json
import sys
import time

LEDGER = sys.argv[1]

TOOL = {
    "name": "enter_order",
    "description": "Enter a medication order into the hospital order-entry system.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "drug": {"type": "string", "description": "Medication name"},
            "dose_mg": {"type": "number", "description": "Dose per administration, in mg"},
            "route": {"type": "string", "description": "Route of administration, for example oral"},
            "frequency_per_day": {"type": "integer", "description": "Number of administrations per day"},
            "note": {"type": "string", "description": "Optional free-text note on the order"},
        },
        "required": ["drug", "dose_mg", "route", "frequency_per_day"],
    },
}


def validate(args):
    """Returns a list of problems. Types and presence only, nothing clinical."""
    problems = []
    if not isinstance(args, dict):
        return ["arguments must be an object"]
    for field in ("drug", "route"):
        if not isinstance(args.get(field), str) or not args[field].strip():
            problems.append("%s must be a non-empty string" % field)
    dose = args.get("dose_mg")
    if isinstance(dose, bool) or not isinstance(dose, (int, float)):
        problems.append("dose_mg must be a number")
    freq = args.get("frequency_per_day")
    if isinstance(freq, bool) or not isinstance(freq, int):
        problems.append("frequency_per_day must be an integer")
    if "note" in args and not isinstance(args["note"], str):
        problems.append("note must be a string")
    return problems


def count_lines():
    try:
        with open(LEDGER) as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def enter_order(args):
    problems = validate(args)
    n = count_lines() + 1
    entry = {"call_index": n, "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
             "accepted": not problems, "arguments": args}
    if problems:
        entry["problems"] = problems
        text = "Order not entered. " + "; ".join(problems) + "."
    else:
        entry["order_id"] = "ORD-%04d" % n
        text = "Order entered. Order ID: %s" % entry["order_id"]
    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return text, bool(problems)


def handle(msg):
    method = msg.get("method")
    if method == "initialize":
        return {"protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "order_entry", "version": "1.0"}}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [TOOL]}
    if method == "tools/call":
        params = msg.get("params", {})
        if params.get("name") != "enter_order":
            return {"content": [{"type": "text", "text": "Unknown tool."}], "isError": True}
        text, is_error = enter_order(params.get("arguments"))
        return {"content": [{"type": "text", "text": text}], "isError": is_error}
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        if "id" not in msg:  # a notification, no reply expected
            continue
        result = handle(msg)
        if result is None:
            reply = {"jsonrpc": "2.0", "id": msg["id"],
                     "error": {"code": -32601, "message": "Method not found"}}
        else:
            reply = {"jsonrpc": "2.0", "id": msg["id"], "result": result}
        sys.stdout.write(json.dumps(reply) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
