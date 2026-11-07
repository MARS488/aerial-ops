#!/usr/bin/env python3
"""Cloud dev capture of the preview. Not part of the local API scenario.

Refuses to start unless CLOUD_DEV_CAPTURE=1. Does not print the access secret.
"""

from __future__ import annotations

import base64
import json
import os
import signal
import socket
import struct
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"
OUT = ROOT / "cloud-capture"


class Cdp:
    def __init__(self, sock: socket.socket) -> None:
        self.sock = sock
        self.buf = b""
        self.next_id = 1

    def call(self, method: str, params: dict | None = None, timeout: float = 20) -> dict:
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
            {"expression": expression, "returnByValue": True},
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
        else:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        header.extend(mask)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(data))
        self.sock.sendall(bytes(header) + masked)

    def _recv(self, deadline: float) -> dict:
        while True:
            frame = self._frame(deadline)
            if frame is not None:
                return json.loads(frame)

    def _frame(self, deadline: float) -> str | None:
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


def chrome_json(port: int, target: str) -> object:
    with urllib.request.urlopen("http://127.0.0.1:%s%s" % (port, target), timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_listen(proc: subprocess.Popen, data: Path) -> dict:
    listen = data / "listen.json"
    if listen.exists():
        listen.unlink()
    deadline = time.time() + 8
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("server exited")
        if listen.exists():
            info = json.loads(listen.read_text(encoding="utf-8"))
            if info.get("pid") == proc.pid:
                return info
        time.sleep(0.05)
    raise RuntimeError("server did not listen")


def page_text(cdp: Cdp) -> str:
    return cdp.evaluate("document.getElementById('client') && !document.getElementById('client').hidden ? document.getElementById('client').innerText : ''") or ""


def click(cdp: Cdp, element_id: str) -> None:
    ok = cdp.evaluate(
        "(function(){var n=document.getElementById('%s'); if(!n || n.hidden) return false; n.click(); return true;})()"
        % element_id
    )
    if ok is not True:
        raise RuntimeError("click failed: " + element_id)


def wait_status(cdp: Cdp, label: str) -> None:
    deadline = time.time() + 8
    while time.time() < deadline:
        current = cdp.evaluate(
            "document.getElementById('job-status') ? document.getElementById('job-status').textContent : ''"
        )
        if current == label:
            return
        time.sleep(0.1)
    raise RuntimeError("status not " + label)


def grab(path: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "x11grab", "-video_size", "1920x1080",
            "-i", ":99.0", "-frames:v", "1", str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=dict(os.environ, DISPLAY=":99"),
    )


def main() -> int:
    if os.environ.get("CLOUD_DEV_CAPTURE") != "1":
        print("SKIPPED_NOT_RUN")
        print("cloud walkthrough is not the local scenario and did not start a browser")
        return 2
    smoke = "--smoke" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%H%M%S")
    data = OUT / ("data-%s" % stamp)
    data.mkdir(parents=True, exist_ok=True)
    log_handle = (OUT / ("server-%s.log" % stamp)).open("w", encoding="utf-8")
    env = os.environ.copy()
    env.pop("SANDBOX_TOKEN", None)
    env["SANDBOX_DATA_DIR"] = str(data)
    env["SANDBOX_PORT"] = "0"
    env["SANDBOX_BIND"] = "127.0.0.1"
    env["DISPLAY"] = ":99"
    server = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=str(ROOT),
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    xvfb = subprocess.Popen(
        ["Xvfb", ":99", "-screen", "0", "1920x1080x24", "-nolisten", "tcp"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    chrome = None
    ffmpeg = None
    try:
        info = wait_listen(server, data)
        secret = (data / "access.token").read_text(encoding="utf-8").strip()
        url = "http://127.0.0.1:%s/" % info["port"]
        profile = OUT / ("chrome-profile-%s" % int(time.time()))
        chrome_log = (OUT / "chrome.log").open("w", encoding="utf-8")
        chrome = subprocess.Popen(
            [
                "google-chrome",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--disable-infobars",
                "--kiosk",
                "--window-position=0,0",
                "--window-size=1920,1080",
                "--remote-debugging-port=9334",
                "--user-data-dir=%s" % profile,
                url,
            ],
            env=env,
            stdout=chrome_log,
            stderr=subprocess.STDOUT,
        )
        page = None
        for _ in range(50):
            try:
                tabs = chrome_json(9334, "/json/list")
                page = next(item for item in tabs if item.get("type") == "page")
                break
            except Exception:
                time.sleep(0.1)
        if page is None:
            raise RuntimeError("chrome did not open")
        cdp = open_cdp(page["webSocketDebuggerUrl"])
        cdp.call("Runtime.enable")
        deadline = time.time() + 15
        while time.time() < deadline:
            if cdp.evaluate("window.__previewBound === true"):
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("preview script did not load")
        cdp.evaluate(
            "document.getElementById('token').value = %s; document.getElementById('unlock').click(); true"
            % json.dumps(secret)
        )
        deadline = time.time() + 20
        opened = False
        while time.time() < deadline:
            if cdp.evaluate("document.getElementById('client') && document.getElementById('client').hidden === false"):
                opened = True
                break
            time.sleep(0.1)
        if not opened:
            try:
                grab(OUT / "open-failed.png")
            except Exception:
                pass
            raise RuntimeError("preview did not open")
        if "Pre-release prototype" not in (cdp.evaluate("document.body.innerText") or ""):
            raise RuntimeError("disclaimer missing")
        if smoke:
            shot = OUT / "smoke.png"
            grab(shot)
            print("smoke=" + str(shot))
            return 0
        raw = OUT / ("raw-%s.mp4" % stamp)
        ffmpeg = subprocess.Popen(
            [
                "ffmpeg", "-y", "-f", "x11grab", "-video_size", "1920x1080",
                "-framerate", "30", "-i", ":99.0",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                "-preset", "veryfast", str(raw),
            ],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        started = time.monotonic()
        marks = []

        def hold(seconds: float, name: str) -> None:
            marks.append({"name": name, "at": round(time.monotonic() - started, 2)})
            time.sleep(seconds)

        hold(14, "open")
        click(cdp, "create-job")
        wait_status(cdp, "Received")
        cdp.evaluate("document.getElementById('job-card').scrollIntoView({block:'center'}); true")
        hold(16, "created")
        click(cdp, "advance")
        wait_status(cdp, "In review")
        hold(14, "in_review")
        click(cdp, "show-castle")
        wait_status(cdp, "In review")
        verified = cdp.evaluate("document.getElementById('verified-count').textContent")
        if verified != "Verified segments: 0":
            raise RuntimeError("verified count changed")
        hold(18, "castle")
        click(cdp, "advance")
        wait_status(cdp, "Reviewed")
        cdp.evaluate("document.getElementById('castle').scrollIntoView({block:'center'}); true")
        hold(14, "reviewed")
        click(cdp, "advance")
        wait_status(cdp, "Fictional test closed")
        hold(14, "closed")
        click(cdp, "record-evidence")
        deadline = time.time() + 8
        while time.time() < deadline:
            note = cdp.evaluate(
                "document.getElementById('evidence-note') ? document.getElementById('evidence-note').textContent : ''"
            ) or ""
            if "No points were added" in note:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("evidence note missing")
        cdp.evaluate("document.getElementById('evidence-note').scrollIntoView({block:'center'}); true")
        hold(16, "evidence")
        cdp.evaluate("document.getElementById('limits').scrollIntoView({block:'center'}); true")
        hold(16, "limits")
        ffmpeg.send_signal(signal.SIGINT)
        ffmpeg.wait(timeout=20)
        ffmpeg = None
        (OUT / "marks.json").write_text(json.dumps(marks, indent=2) + "\n", encoding="utf-8")
        print("raw=" + str(raw))
        print("marks=" + json.dumps(marks))
        return 0
    finally:
        if ffmpeg is not None and ffmpeg.poll() is None:
            ffmpeg.send_signal(signal.SIGINT)
            try:
                ffmpeg.wait(timeout=10)
            except subprocess.TimeoutExpired:
                ffmpeg.kill()
        if chrome is not None and chrome.poll() is None:
            chrome.terminate()
            try:
                chrome.wait(timeout=3)
            except subprocess.TimeoutExpired:
                chrome.kill()
        if server.poll() is None:
            server.send_signal(signal.SIGTERM)
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
        if xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=3)
            except subprocess.TimeoutExpired:
                xvfb.kill()
        log_handle.close()


if __name__ == "__main__":
    sys.exit(main())
