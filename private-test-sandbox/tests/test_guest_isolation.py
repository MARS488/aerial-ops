#!/usr/bin/env python3
"""Loopback rehearsal of guest slots. Not a public deployment test."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"


def start(data: Path, hosted: bool, bind: str = "127.0.0.1", limit: str = "30") -> subprocess.Popen:
    env = os.environ.copy()
    env.pop("SANDBOX_TOKEN", None)
    env["SANDBOX_DATA_DIR"] = str(data)
    env["SANDBOX_PORT"] = "0"
    env["SANDBOX_BIND"] = bind
    env["SANDBOX_HOSTED"] = "1" if hosted else "0"
    env["SANDBOX_GUEST_WRITE_LIMIT"] = limit
    log = (data / "server.log")
    data.mkdir(parents=True, exist_ok=True)
    handle = log.open("w", encoding="utf-8")
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
            if info.get("pid") == proc.pid:
                return info
        time.sleep(0.05)
    raise RuntimeError("no listen file")


def call(port: int, method: str, path: str, body: dict | None = None, headers: dict | None = None) -> tuple[int, dict, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req_headers = {"Content-Type": "application/json"} if body is not None else {}
    if headers:
        req_headers.update(headers)
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
            return response.status, json.loads(raw) if raw else {}, cookie
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"error": "unreadable"}
        return exc.code, payload, ""


def operator_headers(secret: str) -> dict:
    return {
        "Authorization": "Bearer " + secret,
        "X-Sandbox-Account": "sandbox-operator",
    }


def guest_headers(secret: str) -> dict:
    return {"Authorization": "Guest " + secret}


def job_body(mark: str) -> dict:
    return {
        "site_label": "SYNTHETIC-GUEST-" + mark,
        "purpose": "general_assessment",
        "package_code": "quick_look",
        "idempotency_key": "guest-job-" + mark.lower(),
        "correlation_id": "CORR-SYNTHETIC-GUEST-" + mark,
        "note": "fictional guest job",
        "synthetic": True,
    }


def read_secret(data: Path, guest_id: str) -> str:
    return (data / "guests" / ("%s.once" % guest_id)).read_text(encoding="utf-8").strip()


def main() -> int:
    root = ROOT / "run-output-guests"
    if root.exists():
        import shutil
        shutil.rmtree(root)
    refused = start(root / "refuse", hosted=True, bind="0.0.0.0")
    try:
        refused.wait(timeout=5)
    except subprocess.TimeoutExpired:
        stop(refused)
        print("FAIL public bind stayed up")
        return 1
    if refused.returncode == 0:
        print("FAIL public bind exit 0")
        return 1
    stop(refused)

    data = root / "hosted"
    proc = start(data, hosted=True, limit="2")
    try:
        info = listen(proc, data)
        port = info["port"]
        rss = Path("/proc/%s/status" % proc.pid).read_text(encoding="utf-8")
        vmrss = next(line for line in rss.splitlines() if line.startswith("VmRSS:"))
        code, health, _ = call(port, "GET", "/health")
        if code != 200 or health.get("hosted") is not True or health.get("public_bind_enabled") is not False:
            print("FAIL health")
            return 1
        operator = (data / "access.token").read_text(encoding="utf-8").strip()
        headers = operator_headers(operator)
        code, _, _ = call(port, "GET", "/api/guest-jobs", headers=guest_headers(operator))
        if code != 401:
            print("FAIL operator secret accepted as guest")
            return 1
        code, slot_a, _ = call(
            port, "POST", "/api/guest-slots",
            {"label": "FICTIONAL-GUEST-A", "ttl_seconds": 3600},
            headers,
        )
        code_b, slot_b, _ = call(
            port, "POST", "/api/guest-slots",
            {"label": "FICTIONAL-GUEST-B", "ttl_seconds": 3600},
            headers,
        )
        if code != 201 or code_b != 201 or "secret" in slot_a or "secret_hash" in slot_a:
            print("FAIL slot create")
            return 1
        secret_a = read_secret(data, slot_a["guest_id"])
        secret_b = read_secret(data, slot_b["guest_id"])
        if secret_a in json.dumps(slot_a) or secret_b in json.dumps(slot_b):
            print("FAIL secret echoed")
            return 1
        code, created, _ = call(port, "POST", "/api/guest-jobs", job_body("ONE"), guest_headers(secret_a))
        code_list_b, listing_b, _ = call(port, "GET", "/api/guest-jobs", headers=guest_headers(secret_b))
        code_get_b, _, _ = call(
            port, "GET", "/api/guest-jobs/%s" % created.get("id"),
            headers=guest_headers(secret_b),
        )
        if created.get("synthetic") is not True or listing_b.get("jobs") or code_get_b != 404:
            print("FAIL isolation")
            return 1
        code, _, _ = call(port, "GET", "/api/test-records", headers=guest_headers(secret_a))
        if code != 401:
            print("FAIL guest read operator jobs")
            return 1
        code, denied, _ = call(
            port, "POST", "/api/guest-jobs",
            job_body("TWO"),
            dict(guest_headers(secret_a), Origin="https://evil.example"),
        )
        if code != 403:
            print("FAIL origin")
            return 1
        session_code, _session_body, cookie = call(
            port, "POST", "/api/guest-session",
            {"guest_id": slot_a["guest_id"], "secret": secret_a},
        )
        token = cookie.split(";", 1)[0].split("=", 1)[1]
        code, cookie_jobs, _ = call(
            port, "GET", "/api/guest-jobs",
            headers={"Cookie": "guest_session=%s" % token},
        )
        code, csrf, _ = call(
            port, "POST", "/api/guest-jobs",
            job_body("COOKIE"),
            {"Cookie": "guest_session=%s" % token},
        )
        code, cookie_ok, _ = call(
            port, "POST", "/api/guest-jobs",
            job_body("COOKIE"),
            {
                "Cookie": "guest_session=%s" % token,
                "X-Sandbox-Client": "guest",
            },
        )
        if session_code != 200 or not cookie_jobs.get("jobs") or csrf.get("error") != "unauthorized" or cookie_ok.get("status") != "received":
            print("FAIL cookie session")
            return 1
        code, _, _ = call(
            port, "POST", "/api/guest-slots/%s/revoke" % slot_a["guest_id"],
            {},
            headers,
        )
        code, _, _ = call(port, "GET", "/api/guest-jobs", headers=guest_headers(secret_a))
        if code != 401:
            print("FAIL revoke")
            return 1
        code, _, _ = call(
            port, "POST", "/api/guest-slots/%s/reset" % slot_b["guest_id"],
            {},
            headers,
        )
        new_b = read_secret(data, slot_b["guest_id"])
        code, _, _ = call(port, "GET", "/api/guest-jobs", headers=guest_headers(secret_b))
        code_new, _, _ = call(port, "GET", "/api/guest-jobs", headers=guest_headers(new_b))
        if code != 401 or code_new != 200 or new_b == secret_b:
            print("FAIL reset")
            return 1
        db = data / "sandbox.sqlite"
        con = sqlite3.connect(db)
        past = int(time.time()) - 10
        con.execute("UPDATE guests SET expires_at = ? WHERE id = ?", (past, slot_b["guest_id"]))
        con.commit()
        con.close()
        code, _, _ = call(port, "GET", "/api/guest-jobs", headers=guest_headers(new_b))
        if code != 401:
            print("FAIL expiry")
            return 1
        code, _, _ = call(
            port, "POST", "/api/guest-slots",
            {"label": "FICTIONAL-GUEST-C", "ttl_seconds": 3600},
            headers,
        )
        secret_c = read_secret(data, "G-0003")
        first, _, _ = call(port, "POST", "/api/guest-jobs", job_body("C1"), guest_headers(secret_c))
        second, _, _ = call(port, "POST", "/api/guest-jobs", job_body("C2"), guest_headers(secret_c))
        third, limited, _ = call(port, "POST", "/api/guest-jobs", job_body("C3"), guest_headers(secret_c))
        if first != 201 or second != 201 or third != 429 or limited.get("error") != "too_many_writes":
            print("FAIL rate limit")
            return 1
        src = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
        restored = root / "restored.sqlite"
        dst = sqlite3.connect(restored)
        src.backup(dst)
        dst.close()
        src.close()
        check = sqlite3.connect(restored)
        count = check.execute("SELECT COUNT(*) FROM guest_jobs").fetchone()[0]
        check.close()
        if count < 1:
            print("FAIL backup")
            return 1
        print("PASS guest isolation")
        print(vmrss)
        return 0
    finally:
        stop(proc)


if __name__ == "__main__":
    sys.exit(main())
