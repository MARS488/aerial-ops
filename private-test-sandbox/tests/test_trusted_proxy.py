#!/usr/bin/env python3
"""Private trusted-proxy hop. Listens only on 127.0.0.1.

Does not bind 0.0.0.0. Does not print the proxy secret or guest code.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"
ORIGIN = "https://fictional-preview.test"


def config_result(env: dict[str, str]) -> tuple[int, str]:
    child = os.environ.copy()
    for key in (
        "SANDBOX_HOSTED",
        "SANDBOX_BIND",
        "SANDBOX_INGRESS",
        "SANDBOX_PUBLIC_ORIGIN",
        "SANDBOX_PROXY_SHARED_SECRET",
        "SANDBOX_TOKEN",
        "PORT",
    ):
        child.pop(key, None)
    child.update(env)
    child["SANDBOX_ROOT"] = str(ROOT)
    script = (
        "import os, sys\n"
        "sys.path.insert(0, os.environ['SANDBOX_ROOT'])\n"
        "import hosted_preview\n"
        "ing = hosted_preview.load_ingress()\n"
        "sys.stdout.write('%s %s %s\\n' % (ing.mode, ing.bind_host, "
        "'https' if ing.https_cookies else 'plain'))\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(ROOT),
        env=child,
        capture_output=True,
        text=True,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output


def start_app(data: Path, proxy_secret: str) -> subprocess.Popen:
    env = os.environ.copy()
    for key in ("SANDBOX_TOKEN", "PORT"):
        env.pop(key, None)
    env.update(
        {
            "SANDBOX_DATA_DIR": str(data),
            "SANDBOX_PORT": "0",
            "SANDBOX_BIND": "127.0.0.1",
            "SANDBOX_HOSTED": "1",
            "SANDBOX_INGRESS": "trusted-proxy",
            "SANDBOX_PUBLIC_ORIGIN": ORIGIN,
            "SANDBOX_PROXY_SHARED_SECRET": proxy_secret,
        }
    )
    data.mkdir(parents=True, exist_ok=True)
    handle = (data / "server.log").open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=str(ROOT),
        env=env,
        stdout=handle,
        stderr=subprocess.STDOUT,
    )
    proc._log = handle  # type: ignore[attr-defined]
    return proc


def stop(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        proc.send_signal(15)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
    handle = getattr(proc, "_log", None)
    if handle is not None:
        handle.close()


def listen(proc: subprocess.Popen, data: Path) -> dict:
    path = data / "listen.json"
    if path.exists():
        path.unlink()
    deadline = time.time() + 8
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("server exited")
        if path.exists():
            info = json.loads(path.read_text(encoding="utf-8"))
            if info.get("pid") == proc.pid and info.get("host") == "127.0.0.1":
                return info
        time.sleep(0.05)
    raise RuntimeError("no listen file")


class Hop(BaseHTTPRequestHandler):
    upstream = ""
    proxy_secret = ""

    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        self._forward()

    def do_POST(self) -> None:
        self._forward()

    def _forward(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        headers = {}
        for name in (
            "Content-Type",
            "Authorization",
            "Cookie",
            "Origin",
            "X-Sandbox-Client",
            "X-Sandbox-Account",
        ):
            value = self.headers.get(name)
            if value:
                headers[name] = value
        headers["X-Sandbox-Proxy-Secret"] = self.proxy_secret
        headers["X-Forwarded-Proto"] = "https"
        request = urllib.request.Request(
            self.upstream + self.path,
            data=body,
            headers=headers,
            method=self.command,
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                payload = response.read()
                status = response.status
                extra = response.headers
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            status = exc.code
            extra = exc.headers
        self.send_response(status)
        for name in ("Content-Type", "Set-Cookie", "Cache-Control"):
            for value in extra.get_all(name) or []:
                self.send_header(name, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def direct(port: int, path: str, headers: dict | None = None, body: dict | None = None, method: str = "GET") -> tuple[int, dict, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req_headers = dict(headers or {})
    if body is not None:
        req_headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(
        "http://127.0.0.1:%s%s" % (port, path),
        data=data,
        headers=req_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read().decode("utf-8")
            cookie = response.headers.get("Set-Cookie") or ""
            return response.status, _payload(raw), cookie
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        return exc.code, _payload(raw), exc.headers.get("Set-Cookie") or ""


def _payload(raw: str) -> dict:
    try:
        value = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def via(port: int, path: str, headers: dict | None = None, body: dict | None = None, method: str = "GET") -> tuple[int, dict, str]:
    return direct(port, path, headers, body, method)


def main() -> int:
    secret = secrets.token_urlsafe(24)
    if len(secret) < 24:
        print("FAIL secret length")
        return 1
    code, output = config_result(
        {"SANDBOX_HOSTED": "1", "SANDBOX_BIND": "0.0.0.0", "SANDBOX_INGRESS": "loopback"}
    )
    if code == 0 or "0.0.0.0" in output.split():
        print("FAIL loopback accepted a public bind")
        return 1
    code, output = config_result(
        {
            "SANDBOX_HOSTED": "1",
            "SANDBOX_BIND": "0.0.0.0",
            "SANDBOX_INGRESS": "trusted-proxy",
            "SANDBOX_PUBLIC_ORIGIN": "http://fictional-preview.test",
            "SANDBOX_PROXY_SHARED_SECRET": secret,
        }
    )
    if code == 0:
        print("FAIL http origin accepted")
        return 1
    code, output = config_result(
        {
            "SANDBOX_HOSTED": "1",
            "SANDBOX_BIND": "0.0.0.0",
            "SANDBOX_INGRESS": "trusted-proxy",
            "SANDBOX_PUBLIC_ORIGIN": ORIGIN + "/preview",
            "SANDBOX_PROXY_SHARED_SECRET": secret,
        }
    )
    if code == 0:
        print("FAIL origin path accepted")
        return 1
    code, output = config_result(
        {
            "SANDBOX_HOSTED": "1",
            "SANDBOX_BIND": "0.0.0.0",
            "SANDBOX_INGRESS": "trusted-proxy",
            "SANDBOX_PUBLIC_ORIGIN": ORIGIN,
            "SANDBOX_PROXY_SHARED_SECRET": "short-secret",
        }
    )
    if code == 0:
        print("FAIL short proxy secret accepted")
        return 1
    code, output = config_result(
        {
            "SANDBOX_HOSTED": "1",
            "SANDBOX_BIND": "0.0.0.0",
            "SANDBOX_INGRESS": "trusted-proxy",
            "SANDBOX_PUBLIC_ORIGIN": ORIGIN,
            "SANDBOX_PROXY_SHARED_SECRET": secret,
        }
    )
    if code != 0 or secret in output or "trusted-proxy 0.0.0.0 https" not in output:
        print("FAIL trusted-proxy config")
        return 1

    root = ROOT / "run-output-proxy"
    if root.exists():
        import shutil
        shutil.rmtree(root)
    data = root / "data"
    proc = start_app(data, secret)
    hop = None
    try:
        info = listen(proc, data)
        app_port = info["port"]
        Hop.upstream = "http://127.0.0.1:%s" % app_port
        Hop.proxy_secret = secret
        hop = ThreadingHTTPServer(("127.0.0.1", 0), Hop)
        hop_port = hop.server_address[1]
        import threading
        thread = threading.Thread(target=hop.serve_forever, daemon=True)
        thread.start()

        code, health, _ = direct(app_port, "/health")
        if code != 403:
            print("FAIL direct request without proxy secret")
            return 1
        code, _, _ = direct(
            app_port,
            "/health",
            {"X-Forwarded-For": "127.0.0.1", "X-Forwarded-Proto": "https"},
        )
        if code != 403:
            print("FAIL forwarded-for bypass")
            return 1
        code, _, _ = direct(
            app_port,
            "/",
            {
                "X-Sandbox-Proxy-Secret": secret,
                "X-Forwarded-Proto": "http",
                "Origin": ORIGIN,
            },
        )
        if code != 403:
            print("FAIL plain proto admitted")
            return 1
        admitted = {
            "X-Sandbox-Proxy-Secret": secret,
            "X-Forwarded-Proto": "https",
            "Origin": ORIGIN,
        }
        code, health, _ = direct(app_port, "/health", admitted)
        if code != 200 or "account" in health or health.get("ingress") != "trusted-proxy":
            print("FAIL admitted health")
            return 1
        if health.get("https_cookies") is not True or health.get("public_listen") is not False:
            print("FAIL health flags")
            return 1
        code, _, _ = direct(
            app_port,
            "/health",
            {**admitted, "Origin": "https://evil.example"},
        )
        if code != 403:
            print("FAIL foreign origin")
            return 1
        code, page, _ = via(hop_port, "/")
        code_guest, _, _ = via(hop_port, "/guest.html")
        code_evil, _, _ = via(hop_port, "/", {"Origin": "https://evil.example"})
        if code != 200 or code_guest != 200 or code_evil != 403 or "account" in page:
            print("FAIL proxy hop shells")
            return 1
        operator = (data / "access.token").read_text(encoding="utf-8").strip()
        code, slot, _ = via(
            hop_port,
            "/api/guest-slots",
            {
                "Authorization": "Bearer " + operator,
                "X-Sandbox-Account": "sandbox-operator",
                "Content-Type": "application/json",
                "Origin": ORIGIN,
            },
            {"label": "FICTIONAL-GUEST-PROXY", "ttl_seconds": 3600},
            "POST",
        )
        if code != 201 or "secret" in slot:
            print("FAIL proxy slot")
            return 1
        guest_secret = (data / "guests" / ("%s.once" % slot["guest_id"])).read_text(encoding="utf-8").strip()
        code, _body, cookie = via(
            hop_port,
            "/api/guest-session",
            {"Content-Type": "application/json", "Origin": ORIGIN},
            {"guest_id": slot["guest_id"], "secret": guest_secret},
            "POST",
        )
        if code != 200 or "Secure" not in cookie or "HttpOnly" not in cookie:
            print("FAIL secure cookie")
            return 1
        if guest_secret in cookie or secret in cookie:
            print("FAIL secret in cookie")
            return 1
        print("PASS trusted proxy hop")
        return 0
    finally:
        if hop is not None:
            hop.shutdown()
            hop.server_close()
        stop(proc)


if __name__ == "__main__":
    sys.exit(main())
