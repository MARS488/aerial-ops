#!/usr/bin/env python3
"""Capture loopback screenshots. Reads the local secret and does not print it."""

from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"


class Cdp:
    def __init__(self, sock: socket.socket) -> None:
        self.sock = sock
        self.buf = b""
        self.next_id = 1

    def call(self, method: str, params: Optional[dict] = None, timeout: float = 20) -> dict:
        message_id = self.next_id
        self.next_id += 1
        payload = {"id": message_id, "method": method}
        if params:
            payload["params"] = params
        self._send(json.dumps(payload))
        deadline = time.time() + timeout
        while time.time() < deadline:
            message = self._recv(deadline)
            if message.get("id") == message_id:
                if "error" in message:
                    raise RuntimeError("cdp " + method + " failed")
                return message.get("result") or {}
        raise RuntimeError("cdp timeout " + method)

    def evaluate(self, expression: str) -> object:
        result = self.call(
            "Runtime.evaluate",
            {"expression": expression, "awaitPromise": True, "returnByValue": True},
        )
        if "exceptionDetails" in result:
            raise RuntimeError("page script failed")
        return (result.get("result") or {}).get("value")

    def _send(self, text: str) -> None:
        data = text.encode("utf-8")
        mask = os.urandom(4)
        header = bytearray([0x81])
        length = len(data)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        header.extend(mask)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(data))
        self.sock.sendall(bytes(header) + masked)

    def _recv(self, deadline: float) -> dict:
        while True:
            frame = self._frame(deadline)
            if frame is None:
                continue
            return json.loads(frame)

    def _frame(self, deadline: float) -> Optional[str]:
        while len(self.buf) < 2:
            self._read(deadline)
        first, second = self.buf[0], self.buf[1]
        length = second & 0x7F
        offset = 2
        if length == 126:
            while len(self.buf) < 4:
                self._read(deadline)
            length = struct.unpack("!H", self.buf[2:4])[0]
            offset = 4
        elif length == 127:
            while len(self.buf) < 10:
                self._read(deadline)
            length = struct.unpack("!Q", self.buf[2:10])[0]
            offset = 10
        while len(self.buf) < offset + length:
            self._read(deadline)
        payload = self.buf[offset : offset + length]
        self.buf = self.buf[offset + length :]
        opcode = first & 0x0F
        if opcode == 8:
            raise RuntimeError("cdp socket closed")
        if opcode != 1:
            return None
        return payload.decode("utf-8")

    def _read(self, deadline: float) -> None:
        remaining = deadline - time.time()
        if remaining <= 0:
            raise RuntimeError("cdp read timeout")
        self.sock.settimeout(remaining)
        chunk = self.sock.recv(65536)
        if not chunk:
            raise RuntimeError("cdp socket closed")
        self.buf += chunk


def open_cdp(debugger: str) -> Cdp:
    host_port, path = debugger.split("://", 1)[1].split("/", 1)
    host, port = host_port.split(":")
    sock = socket.create_connection((host, int(port)), timeout=10)
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    request = (
        "GET /%s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\n"
        "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n" % (path, host_port, key)
    )
    sock.sendall(request.encode("ascii"))
    buf = b""
    while b"\r\n\r\n" not in buf:
        buf += sock.recv(4096)
    if b" 101 " not in buf.split(b"\r\n", 1)[0]:
        raise RuntimeError("cdp upgrade failed")
    return Cdp(sock)


def chrome_json(port: int, method: str, target: str) -> dict:
    req = urllib.request.Request("http://127.0.0.1:%s%s" % (port, target), method=method)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def shot(cdp: Cdp, path: Path) -> None:
    result = cdp.call("Page.captureScreenshot", {"format": "png"})
    path.write_bytes(base64.b64decode(result["data"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--shots", required=True)
    args = parser.parse_args()
    data = Path(args.data_dir)
    shots = Path(args.shots)
    shots.mkdir(parents=True, exist_ok=True)
    secret = (data / "access.token").read_text(encoding="utf-8").strip()
    if len(secret) < 16:
        print("secret file unusable")
        return 1
    log = shots / "browser-server.log"
    log_handle = log.open("w", encoding="utf-8")
    env = os.environ.copy()
    env.pop("SANDBOX_TOKEN", None)
    env["SANDBOX_DATA_DIR"] = str(data)
    env["SANDBOX_PORT"] = "0"
    env["SANDBOX_BIND"] = "127.0.0.1"
    server = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=str(ROOT),
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    chrome = None
    try:
        listen = data / "listen.json"
        if listen.exists():
            listen.unlink()
        deadline = time.time() + 8
        info = None
        while time.time() < deadline:
            if server.poll() is not None:
                print("server exited before screenshots")
                return 1
            if listen.exists():
                info = json.loads(listen.read_text(encoding="utf-8"))
                if info.get("pid") == server.pid:
                    break
                info = None
            time.sleep(0.05)
        if info is None:
            print("server did not listen")
            return 1
        app = "http://127.0.0.1:%s/" % info["port"]
        debug_port = 9333
        profile = shots / "chrome-profile"
        chrome = subprocess.Popen(
            [
                "google-chrome",
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--remote-debugging-port=%s" % debug_port,
                "--user-data-dir=%s" % profile,
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        version = None
        for _ in range(50):
            try:
                version = chrome_json(debug_port, "GET", "/json/version")
                break
            except Exception:
                time.sleep(0.1)
        if version is None:
            print("chrome debugger did not start")
            return 1
        try:
            page = chrome_json(debug_port, "PUT", "/json/new?" + app)
        except Exception:
            page = chrome_json(debug_port, "GET", "/json/new?" + app)
        cdp = open_cdp(page["webSocketDebuggerUrl"])
        cdp.call("Page.enable")
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1280, "height": 900, "deviceScaleFactor": 1, "mobile": False},
        )
        cdp.call("Page.navigate", {"url": app})
        ready = False
        for _ in range(40):
            if cdp.evaluate("Boolean(window.__sandboxReady)"):
                ready = True
                break
            time.sleep(0.1)
        if not ready:
            print("page did not become ready")
            return 1
        shot(cdp, shots / "01_health_before_secret.png")
        cdp.evaluate(
            "document.getElementById('token').value = %s; "
            "document.getElementById('unlock').click(); true" % json.dumps(secret)
        )
        seen = False
        for _ in range(40):
            state = cdp.evaluate("document.body.textContent") or ""
            if "TS-0001" in state and "in_review" in state:
                seen = True
                break
            time.sleep(0.1)
        if not seen:
            print("shared job was not visible after unlock")
            return 1
        cdp.evaluate("document.querySelector('[data-tab=review]').click(); true")
        time.sleep(0.2)
        shot(cdp, shots / "02_review_same_job.png")
        cdp.evaluate("document.querySelector('[data-tab=castle]').click(); true")
        time.sleep(0.3)
        castle_ok = cdp.evaluate(
            "document.getElementById('green-count').textContent + '|' + "
            "document.querySelectorAll('.is-green').length + '|' + "
            "document.querySelectorAll('.board-row').length + '|' + "
            "document.getElementById('shared-job').textContent"
        )
        if castle_ok != "Green segments: 0|0|19|Shared job: TS-0001 status=in_review correlation=CORR-SYNTHETIC-JOB-0001":
            print("castle display mismatch")
            return 1
        shot(cdp, shots / "03_new_castle_not_green.png")
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True},
        )
        time.sleep(0.2)
        shot(cdp, shots / "04_castle_narrow.png")
        print("screenshots=4")
        return 0
    finally:
        if chrome is not None and chrome.poll() is None:
            chrome.terminate()
            try:
                chrome.wait(timeout=3)
            except subprocess.TimeoutExpired:
                chrome.kill()
        if server.poll() is None:
            server.send_signal(15)
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
        log_handle.close()


if __name__ == "__main__":
    sys.exit(main())
