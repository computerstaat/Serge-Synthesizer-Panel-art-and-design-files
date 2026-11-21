#!/usr/bin/env python3
"""Talk to Front Panel Designer's built-in MCP server (FPD-MCP, TCP 127.0.0.1:5757, Content-Length framing).
Standard library only. Used by fpd_discover.py and fpd_build.py."""
import json
import os
import socket

HOST = os.environ.get("FPD_MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("FPD_MCP_PORT", "5757"))


class FPD:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=120)
        self.buf = b""
        self.n = 0
        self.info = self.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                "clientInfo": {"name": "serge-fpd-builder", "version": "1"}})
        self.notify("notifications/initialized")

    def _send(self, msg):
        body = json.dumps(msg).encode()
        self.s.sendall(b"Content-Length: %d\r\n\r\n" % len(body) + body)

    def _recv(self):
        while True:
            sep = self.buf.find(b"\r\n\r\n")
            if sep >= 0:
                n = None
                for line in self.buf[:sep].split(b"\r\n"):
                    k, _, v = line.partition(b":")
                    if k.strip().lower() == b"content-length":
                        n = int(v)
                if n is not None and len(self.buf) >= sep + 4 + n:
                    body = self.buf[sep + 4: sep + 4 + n]
                    self.buf = self.buf[sep + 4 + n:]
                    return json.loads(body)
            chunk = self.s.recv(65536)
            if not chunk:
                raise ConnectionError("Front Panel Designer closed the connection")
            self.buf += chunk

    def notify(self, method, params=None):
        self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def request(self, method, params=None):
        self.n += 1
        mid = self.n
        self._send({"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}})
        while True:
            m = self._recv()
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError("%s: %s" % (method, m["error"]))
                return m.get("result")

    def tools(self):
        return self.request("tools/list").get("tools", [])

    def call(self, name, args=None):
        r = self.request("tools/call", {"name": name, "arguments": args or {}})
        text = "".join(c.get("text", "") for c in (r or {}).get("content", []) if c.get("type") == "text")
        if r and r.get("isError"):
            raise RuntimeError("%s failed: %s" % (name, text))
        try:
            return json.loads(text)
        except Exception:
            return text
