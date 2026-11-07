"""Hosted-preview rehearsal. Off unless SANDBOX_HOSTED=1.

Default ingress is loopback and refuses every bind except 127.0.0.1.
Trusted-proxy mode is a private rehearsal: it requires an https origin
and a long proxy secret, and it still does not purchase, deploy, or invite.
The hosted candidate stays FAIL until a real provider, TLS name, and
restore-off-service check are signed by someone else.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

LABEL_RE = re.compile(r"^FICTIONAL-GUEST-[A-Z0-9-]{1,24}$")
SITE_RE = re.compile(r"^SYNTHETIC-[A-Z0-9][A-Z0-9-]{1,40}$")
REQUEST_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
CORR_RE = re.compile(r"^CORR-SYNTHETIC-[A-Z0-9][A-Z0-9-]{2,40}$")
NOTE_RE = re.compile(r"^[A-Za-z0-9 .,'-]{0,200}$")
GUEST_ID_RE = re.compile(r"^G-\d{4,}$")
JOB_ID_RE = re.compile(r"^GJ-\d{4,}$")


def hosted_enabled() -> bool:
    return os.environ.get("SANDBOX_HOSTED") == "1"


GUEST_NOTES = {
    "",
    "fictional guest job",
    "fictional review",
    "fictional review step",
    "fictional evidence",
}


class Ingress:
    def __init__(self, mode: str, bind_host: str, public_origin: str, https_cookies: bool, proxy_secret: str) -> None:
        self.mode = mode
        self.bind_host = bind_host
        self.public_origin = public_origin
        self.https_cookies = https_cookies
        self.proxy_secret = proxy_secret


def _https_origin(origin: str) -> bool:
    if not origin.startswith("https://"):
        return False
    rest = origin[len("https://") :]
    return bool(rest) and "/" not in rest and " " not in rest and "@" not in rest


def load_ingress() -> Ingress:
    """Fail closed. Public bind is allowed only for an explicit trusted-proxy config."""
    hosted = hosted_enabled()
    ingress = os.environ.get("SANDBOX_INGRESS", "loopback")
    bind = os.environ.get("SANDBOX_BIND", "127.0.0.1")
    origin = os.environ.get("SANDBOX_PUBLIC_ORIGIN", "").strip()
    secret = os.environ.get("SANDBOX_PROXY_SHARED_SECRET", "")
    if ingress == "loopback":
        if bind != "127.0.0.1":
            raise SystemExit(
                "Refusing non-loopback bind. Trusted-proxy mode was not selected."
            )
        return Ingress("loopback", "127.0.0.1", "", False, "")
    if not hosted or ingress != "trusted-proxy":
        raise SystemExit("Ingress configuration is incomplete. Fail closed.")
    if not _https_origin(origin):
        raise SystemExit(
            "SANDBOX_PUBLIC_ORIGIN must be an https origin with no path. Fail closed."
        )
    if len(secret) < 24:
        raise SystemExit(
            "SANDBOX_PROXY_SHARED_SECRET is missing or short. Fail closed. Value not printed."
        )
    if bind not in ("127.0.0.1", "0.0.0.0"):
        raise SystemExit("SANDBOX_BIND is not allowed. Fail closed.")
    return Ingress("trusted-proxy", bind, origin, True, secret)


def proxy_headers_ok(headers: Any, ingress: Ingress) -> bool:
    if ingress.mode != "trusted-proxy":
        return True
    presented = headers.get("X-Sandbox-Proxy-Secret") or ""
    if len(presented) != len(ingress.proxy_secret):
        return False
    if not hmac.compare_digest(presented, ingress.proxy_secret):
        return False
    return (headers.get("X-Forwarded-Proto") or "").lower() == "https"


def origin_allowed(origin: Optional[str], ingress: Ingress, port: int) -> bool:
    if not origin:
        return True
    if ingress.mode == "trusted-proxy":
        return origin == ingress.public_origin
    return origin in {
        "http://127.0.0.1:%s" % port,
        "http://localhost:%s" % port,
    }


def utc_iso(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _match(presented: str, stored_hex: str) -> bool:
    if not presented or not stored_hex:
        return False
    return hmac.compare_digest(_digest(presented), stored_hex)


class GuestBook:
    def __init__(self, conn: sqlite3.Connection, lock: Any, data_dir: Path) -> None:
        self.conn = conn
        self.lock = lock
        self.data_dir = data_dir
        self._init()

    def _init(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS guests (
              id TEXT PRIMARY KEY,
              label TEXT NOT NULL UNIQUE,
              secret_hash TEXT NOT NULL,
              expires_at INTEGER NOT NULL,
              revoked INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS guest_sessions (
              token_hash TEXT PRIMARY KEY,
              guest_id TEXT NOT NULL,
              expires_at INTEGER NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS guest_jobs (
              id TEXT PRIMARY KEY,
              guest_id TEXT NOT NULL,
              site_label TEXT NOT NULL,
              purpose TEXT NOT NULL,
              package_code TEXT NOT NULL,
              status TEXT NOT NULL,
              idempotency_key TEXT NOT NULL,
              correlation_id TEXT NOT NULL,
              note TEXT NOT NULL,
              synthetic INTEGER NOT NULL CHECK (synthetic = 1),
              billing_state TEXT NOT NULL,
              amount_cents INTEGER,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              UNIQUE (guest_id, idempotency_key)
            );
            CREATE TABLE IF NOT EXISTS guest_attempts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              guest_label TEXT NOT NULL,
              created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS guest_writes (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              guest_id TEXT NOT NULL,
              created_at INTEGER NOT NULL
            );
            """
        )
        self.conn.commit()

    def create_slot(self, label: str, ttl_seconds: int) -> dict[str, Any]:
        if not LABEL_RE.fullmatch(label or ""):
            return _error(400, "validation_failed")
        if not isinstance(ttl_seconds, int) or isinstance(ttl_seconds, bool):
            return _error(400, "validation_failed")
        if ttl_seconds < 60 or ttl_seconds > 7 * 24 * 3600:
            return _error(400, "validation_failed")
        secret = secrets.token_urlsafe(32)
        now = int(time.time())
        expires = now + ttl_seconds
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            count = self.conn.execute("SELECT COUNT(*) AS n FROM guests").fetchone()["n"]
            guest_id = "G-%04d" % (count + 1)
            try:
                self.conn.execute(
                    "INSERT INTO guests (id, label, secret_hash, expires_at, revoked, created_at) "
                    "VALUES (?, ?, ?, ?, 0, ?)",
                    (guest_id, label, _digest(secret), expires, utc_iso(now)),
                )
            except sqlite3.IntegrityError:
                self.conn.rollback()
                return _error(409, "conflict")
            self.conn.commit()
        self._write_secret(guest_id, secret)
        return {
            "status": 201,
            "body": {
                "guest_id": guest_id,
                "label": label,
                "expires_at": utc_iso(expires),
                "secret_file": "guests/%s.once" % guest_id,
                "synthetic_only": True,
                "revocable": True,
            },
        }

    def revoke(self, guest_id: str) -> dict[str, Any]:
        if not GUEST_ID_RE.fullmatch(guest_id or ""):
            return _error(404, "not_found")
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            row = self.conn.execute("SELECT id FROM guests WHERE id = ?", (guest_id,)).fetchone()
            if row is None:
                self.conn.rollback()
                return _error(404, "not_found")
            self.conn.execute("UPDATE guests SET revoked = 1 WHERE id = ?", (guest_id,))
            self.conn.execute("DELETE FROM guest_sessions WHERE guest_id = ?", (guest_id,))
            self.conn.commit()
        return {"status": 200, "body": {"guest_id": guest_id, "revoked": True}}

    def reset(self, guest_id: str) -> dict[str, Any]:
        if not GUEST_ID_RE.fullmatch(guest_id or ""):
            return _error(404, "not_found")
        secret = secrets.token_urlsafe(32)
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            row = self.conn.execute(
                "SELECT expires_at, revoked FROM guests WHERE id = ?", (guest_id,)
            ).fetchone()
            if row is None:
                self.conn.rollback()
                return _error(404, "not_found")
            self.conn.execute(
                "UPDATE guests SET secret_hash = ?, revoked = 0 WHERE id = ?",
                (_digest(secret), guest_id),
            )
            self.conn.execute("DELETE FROM guest_sessions WHERE guest_id = ?", (guest_id,))
            self.conn.commit()
            expires = row["expires_at"]
        self._write_secret(guest_id, secret)
        return {
            "status": 200,
            "body": {
                "guest_id": guest_id,
                "secret_file": "guests/%s.once" % guest_id,
                "expires_at": utc_iso(expires),
                "previous_sessions_revoked": True,
            },
        }

    def list_slots(self) -> dict[str, Any]:
        with self.lock:
            rows = self.conn.execute(
                "SELECT id, label, expires_at, revoked FROM guests ORDER BY id"
            ).fetchall()
        return {
            "status": 200,
            "body": {
                "guests": [
                    {
                        "guest_id": row["id"],
                        "label": row["label"],
                        "expires_at": utc_iso(row["expires_at"]),
                        "revoked": bool(row["revoked"]),
                    }
                    for row in rows
                ]
            },
        }

    def open_session(self, guest_id: str, secret: str, data_dir_cookie: bool) -> dict[str, Any]:
        if not self._attempt_allowed(guest_id):
            return _error(429, "too_many_attempts")
        guest = self._valid_guest(guest_id, secret)
        if guest is None:
            self._record_attempt(guest_id)
            return _error(401, "unauthorized")
        token = secrets.token_urlsafe(32)
        now = int(time.time())
        expires = min(guest["expires_at"], now + 12 * 3600)
        with self.lock:
            self.conn.execute(
                "INSERT INTO guest_sessions (token_hash, guest_id, expires_at, created_at) "
                "VALUES (?, ?, ?, ?)",
                (_digest(token), guest_id, expires, utc_iso(now)),
            )
            self.conn.commit()
        result = {
            "status": 200,
            "body": {
                "guest_id": guest_id,
                "expires_at": utc_iso(expires),
                "synthetic_only": True,
            },
        }
        if data_dir_cookie:
            result["cookie"] = token
            result["cookie_max_age"] = max(60, expires - now)
        return result

    def create_job(self, guest_id: str, body: dict[str, Any]) -> dict[str, Any]:
        site = body.get("site_label")
        purpose = body.get("purpose")
        package = body.get("package_code")
        key = body.get("idempotency_key")
        correlation = body.get("correlation_id")
        note = body.get("note") or ""
        allowed = {
            "site_label",
            "purpose",
            "package_code",
            "idempotency_key",
            "correlation_id",
            "note",
            "synthetic",
        }
        if set(body) - allowed or body.get("synthetic") is not True:
            return _error(400, "validation_failed")
        if purpose not in {"general_assessment", "storm_documentation"}:
            return _error(400, "validation_failed")
        if package not in {"quick_look", "full_assessment", "seasonal_plan"}:
            return _error(400, "validation_failed")
        if not isinstance(site, str) or not SITE_RE.fullmatch(site):
            return _error(400, "validation_failed")
        if not isinstance(key, str) or not REQUEST_RE.fullmatch(key):
            return _error(400, "validation_failed")
        if not isinstance(correlation, str) or not CORR_RE.fullmatch(correlation):
            return _error(400, "validation_failed")
        if note not in GUEST_NOTES:
            return _error(400, "validation_failed")
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            existing = self.conn.execute(
                "SELECT * FROM guest_jobs WHERE guest_id = ? AND idempotency_key = ?",
                (guest_id, key),
            ).fetchone()
            if existing is not None:
                same = (
                    existing["site_label"] == site
                    and existing["purpose"] == purpose
                    and existing["package_code"] == package
                    and existing["correlation_id"] == correlation
                    and existing["note"] == note
                )
                self.conn.commit()
                if not same:
                    return _error(409, "conflict")
                payload = _job(existing)
                payload["deduped"] = True
                return {"status": 200, "body": payload}
            count = self.conn.execute(
                "SELECT COUNT(*) AS n FROM guest_jobs WHERE guest_id = ?", (guest_id,)
            ).fetchone()["n"]
            if count >= 20:
                self.conn.rollback()
                return _error(429, "too_many_jobs")
            self.conn.commit()
        if not self._write_allowed(guest_id):
            return _error(429, "too_many_writes")
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            job_id = "GJ-%04d" % (
                self.conn.execute("SELECT COUNT(*) AS n FROM guest_jobs").fetchone()["n"] + 1
            )
            now = utc_iso(int(time.time()))
            self.conn.execute(
                """
                INSERT INTO guest_jobs (
                  id, guest_id, site_label, purpose, package_code, status,
                  idempotency_key, correlation_id, note, synthetic, billing_state,
                  amount_cents, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'received', ?, ?, ?, 1, 'disabled', NULL, ?, ?)
                """,
                (job_id, guest_id, site, purpose, package, key, correlation, note, now, now),
            )
            row = self.conn.execute("SELECT * FROM guest_jobs WHERE id = ?", (job_id,)).fetchone()
            self.conn.commit()
        payload = _job(row)
        payload["deduped"] = False
        return {"status": 201, "body": payload}

    def list_jobs(self, guest_id: str) -> dict[str, Any]:
        with self.lock:
            rows = self.conn.execute(
                "SELECT * FROM guest_jobs WHERE guest_id = ? ORDER BY id", (guest_id,)
            ).fetchall()
        return {"status": 200, "body": {"jobs": [_job(row) for row in rows]}}

    def get_job(self, guest_id: str, job_id: str) -> dict[str, Any]:
        if not JOB_ID_RE.fullmatch(job_id or ""):
            return _error(404, "not_found")
        with self.lock:
            row = self.conn.execute(
                "SELECT * FROM guest_jobs WHERE id = ? AND guest_id = ?",
                (job_id, guest_id),
            ).fetchone()
        if row is None:
            return _error(404, "not_found")
        return {"status": 200, "body": _job(row)}

    def identify(self, secret: Optional[str], session_token: Optional[str]) -> Optional[str]:
        now = int(time.time())
        with self.lock:
            if session_token:
                row = self.conn.execute(
                    "SELECT guest_id, expires_at FROM guest_sessions WHERE token_hash = ?",
                    (_digest(session_token),),
                ).fetchone()
                if row is None or row["expires_at"] < now:
                    return None
                guest = self.conn.execute(
                    "SELECT revoked, expires_at FROM guests WHERE id = ?",
                    (row["guest_id"],),
                ).fetchone()
                if guest is None or guest["revoked"] or guest["expires_at"] < now:
                    return None
                return row["guest_id"]
            if not secret:
                return None
            rows = self.conn.execute(
                "SELECT id, secret_hash, revoked, expires_at FROM guests"
            ).fetchall()
            self.conn.execute("DELETE FROM guest_attempts WHERE created_at < ?", (now - 600,))
            self.conn.execute("DELETE FROM guest_sessions WHERE expires_at < ?", (now,))
            self.conn.commit()
        for row in rows:
            if row["revoked"] or row["expires_at"] < now:
                continue
            if _match(secret, row["secret_hash"]):
                return row["id"]
        self._record_attempt("direct-header")
        return None

    def direct_header_blocked(self) -> bool:
        return not self._attempt_allowed("direct-header")

    def _valid_guest(self, guest_id: str, secret: str) -> Optional[sqlite3.Row]:
        now = int(time.time())
        with self.lock:
            row = self.conn.execute("SELECT * FROM guests WHERE id = ?", (guest_id,)).fetchone()
        if row is None or row["revoked"] or row["expires_at"] < now:
            return None
        if not _match(secret, row["secret_hash"]):
            return None
        return row

    def _attempt_allowed(self, guest_id: str) -> bool:
        cutoff = int(time.time()) - 600
        with self.lock:
            count = self.conn.execute(
                "SELECT COUNT(*) AS n FROM guest_attempts WHERE guest_label = ? AND created_at >= ?",
                (guest_id, cutoff),
            ).fetchone()["n"]
        return count < 8

    def _record_attempt(self, guest_id: str) -> None:
        with self.lock:
            self.conn.execute(
                "INSERT INTO guest_attempts (guest_label, created_at) VALUES (?, ?)",
                (guest_id, int(time.time())),
            )
            self.conn.commit()

    def _write_allowed(self, guest_id: str) -> bool:
        limit = int(os.environ.get("SANDBOX_GUEST_WRITE_LIMIT", "30"))
        now = int(time.time())
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            self.conn.execute("DELETE FROM guest_writes WHERE created_at < ?", (now - 60,))
            count = self.conn.execute(
                "SELECT COUNT(*) AS n FROM guest_writes WHERE guest_id = ?",
                (guest_id,),
            ).fetchone()["n"]
            if count >= limit:
                self.conn.commit()
                return False
            self.conn.execute(
                "INSERT INTO guest_writes (guest_id, created_at) VALUES (?, ?)",
                (guest_id, now),
            )
            self.conn.commit()
        return True

    def _write_secret(self, guest_id: str, secret: str) -> None:
        folder = self.data_dir / "guests"
        folder.mkdir(parents=True, exist_ok=True)
        os.chmod(folder, 0o700)
        path = folder / ("%s.once" % guest_id)
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(secret + "\n")
        os.chmod(path, 0o600)


def _job(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "guest_id": row["guest_id"],
        "site_label": row["site_label"],
        "purpose": row["purpose"],
        "package_code": row["package_code"],
        "status": row["status"],
        "idempotency_key": row["idempotency_key"],
        "correlation_id": row["correlation_id"],
        "note": row["note"],
        "synthetic": True,
        "billing_state": "disabled",
        "amount_cents": None,
        "invoice": None,
    }


def _error(status: int, code: str) -> dict[str, Any]:
    return {"status": status, "body": {"error": code}}


def cookie_token(header: str) -> Optional[str]:
    if not header:
        return None
    for part in header.split(";"):
        name, _, value = part.strip().partition("=")
        if name == "guest_session" and value:
            return value
    return None


def dispatch(handler: Any, method: str, path: str) -> None:
    book: GuestBook = handler.server.guest_book
    if method == "POST" and path == "/api/guest-session":
        _session(handler, book)
        return
    if path.startswith("/api/guest-slots"):
        if not handler._authorized():
            handler._send(401, {"error": "unauthorized"})
            return
        _slots(handler, book, method, path)
        return
    guest_id = _guest_from_request(handler, book, method)
    if guest_id == "":
        return
    if guest_id is None:
        handler._send(401, {"error": "unauthorized"})
        return
    if method == "GET" and path == "/api/guest-jobs":
        result = book.list_jobs(guest_id)
    elif method == "POST" and path == "/api/guest-jobs":
        body, error = handler._json_body()
        if error is not None or body is None:
            handler._send(400, {"error": "invalid_json"})
            return
        result = book.create_job(guest_id, body)
    else:
        match = re.fullmatch(r"/api/guest-jobs/(GJ-\d{4,})", path)
        if method == "GET" and match:
            result = book.get_job(guest_id, match.group(1))
        else:
            handler._send(404, {"error": "not_found"})
            return
    handler._send(result["status"], result["body"])


def _session(handler: Any, book: GuestBook) -> None:
    body, error = handler._json_body()
    if error is not None or body is None:
        handler._send(400, {"error": "invalid_json"})
        return
    guest_id = body.get("guest_id")
    secret = body.get("secret")
    if not isinstance(guest_id, str) or not isinstance(secret, str):
        handler._send(400, {"error": "validation_failed"})
        return
    result = book.open_session(guest_id, secret, data_dir_cookie=True)
    if result["status"] != 200:
        handler._send(result["status"], result["body"])
        return
    token = result.pop("cookie")
    max_age = result.pop("cookie_max_age")
    cookie = "guest_session=%s; HttpOnly; SameSite=Strict; Path=/; Max-Age=%s" % (
        token,
        max_age,
    )
    ingress = getattr(getattr(handler, "server", None), "ingress", None)
    if ingress is not None and ingress.https_cookies:
        cookie += "; Secure"
    handler._send(200, result["body"], extra_headers=[("Set-Cookie", cookie)])


def _slots(handler: Any, book: GuestBook, method: str, path: str) -> None:
    if method == "GET" and path == "/api/guest-slots":
        result = book.list_slots()
        handler._send(result["status"], result["body"])
        return
    if method == "POST" and path == "/api/guest-slots":
        body, error = handler._json_body()
        if error is not None or body is None:
            handler._send(400, {"error": "invalid_json"})
            return
        label = body.get("label")
        ttl = body.get("ttl_seconds", 7 * 24 * 3600)
        if not isinstance(label, str):
            handler._send(400, {"error": "validation_failed"})
            return
        result = book.create_slot(label, ttl)
        handler._send(result["status"], result["body"])
        return
    revoke = re.fullmatch(r"/api/guest-slots/(G-\d{4,})/revoke", path)
    reset = re.fullmatch(r"/api/guest-slots/(G-\d{4,})/reset", path)
    if method == "POST" and revoke:
        result = book.revoke(revoke.group(1))
        handler._send(result["status"], result["body"])
        return
    if method == "POST" and reset:
        result = book.reset(reset.group(1))
        handler._send(result["status"], result["body"])
        return
    handler._send(404, {"error": "not_found"})


def _guest_from_request(handler: Any, book: GuestBook, method: str) -> Optional[str]:
    header = handler.headers.get("Authorization") or ""
    secret = header[6:].strip() if header.startswith("Guest ") else None
    session = cookie_token(handler.headers.get("Cookie") or "")
    if session and method in {"POST", "PUT", "DELETE"}:
        if handler.headers.get("X-Sandbox-Client") != "guest":
            return None
    if handler._authorized():
        return None
    if secret and book.direct_header_blocked():
        handler._send(429, {"error": "too_many_attempts"})
        return ""
    found = book.identify(secret, session)
    return found
