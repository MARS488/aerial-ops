#!/usr/bin/env python3
"""Private loopback test sandbox. Python standard library only.

Listens on 127.0.0.1. Does not call Notion, Dropbox, Stripe, Base44,
or any other network service. Does not print the access secret.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import hosted_preview
import os
import re
import secrets
import signal
import sqlite3
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
FIXTURE_PATH = ROOT / "fixtures" / "castle_board_fixture.json"
BIND_HOST = "127.0.0.1"
ACCOUNT = "sandbox-operator"
MAX_BODY = 8192
LIVE_INTAKE_ENABLED = False
MONEY_ACTIONS = False

PURPOSES = {"general_assessment", "storm_documentation"}
PACKAGES = {"quick_look", "full_assessment", "seasonal_plan"}
STATUSES = {"received", "in_review", "reviewed", "closed_test", "rejected"}
TRANSITIONS = {
    "received": {"in_review", "rejected"},
    "in_review": {"reviewed", "rejected"},
    "reviewed": {"closed_test"},
    "closed_test": set(),
    "rejected": set(),
}
CREATE_KEYS = {
    "site_label",
    "purpose",
    "package_code",
    "idempotency_key",
    "correlation_id",
    "note",
    "synthetic",
}
STATUS_KEYS = {"status", "note", "dedup_key"}
SCORE_KEYS = {
    "dedup_key",
    "subject",
    "evidence_ref",
    "review_state",
    "points",
    "synthetic",
    "note",
    "correlation_id",
}
RULE_KEYS = {"evidence_verdict", "proof_url_present", "preserved_status"}
SUBJECTS = {"civilitysync-test", "stronghold-new-prototype"}
PRESERVED_STATUSES = {"Built", "In progress", "Not started"}
SITE_RE = re.compile(r"^SYNTHETIC-[A-Z0-9][A-Z0-9-]{1,40}$")
REQUEST_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
CORR_RE = re.compile(r"^CORR-SYNTHETIC-[A-Z0-9][A-Z0-9-]{2,40}$")
DEDUP_RE = re.compile(r"^[A-Za-z0-9_.:-]{8,80}$")
NOTE_RE = re.compile(r"^[A-Za-z0-9 .,'-]{0,200}$")
EVIDENCE_RE = re.compile(r"^[a-z0-9:._-]{4,80}$")
PHONE_RE = re.compile(r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}")
STREET_RE = re.compile(
    r"\b\d{1,6}\s+[A-Za-z0-9.'-]+\s+"
    r"(st|street|ave|avenue|rd|road|dr|drive|ln|lane|blvd|way|ct|court)\b",
    re.IGNORECASE,
)

STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/guest.html": ("guest.html", "text/html; charset=utf-8"),
    "/guest.js": ("guest.js", "text/javascript; charset=utf-8"),
    "/guest.css": ("guest.css", "text/css; charset=utf-8"),
}


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def digest(value: str) -> bytes:
    return hashlib.sha256(value.encode("utf-8")).digest()


def same_secret(presented: str, expected: str) -> bool:
    if len(presented) > 200 or len(expected) > 200:
        return False
    return hmac.compare_digest(digest(presented), digest(expected))


def display_for(evidence_verdict: str) -> str:
    """Wall color follows the explicit verdict only. Proof URL is ignored."""
    if evidence_verdict == "EXPLICIT_PASS":
        return "green"
    return "not_green"


def looks_like_identifier(text: str) -> bool:
    if "@" in text or "://" in text:
        return True
    if PHONE_RE.search(text):
        return True
    if STREET_RE.search(text):
        return True
    return False


def load_fixture() -> dict[str, Any]:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if data.get("fixture_kind") != "TEST_UNVERIFIED_COPY":
        raise SystemExit("castle fixture is missing its test/unverified label")
    rows = data.get("rows") or []
    if len(rows) != 19:
        raise SystemExit("castle fixture must contain the 19 preserved rows")
    return data


def castle_board() -> dict[str, Any]:
    raw = load_fixture()
    gap = raw["gap_matrix_url"]
    rows = []
    preserved = {"Built": 0, "In progress": 0, "Not started": 0}
    for item in raw["rows"]:
        status = item["preserved_status"]
        preserved[status] = preserved.get(status, 0) + 1
        verdict = "UNVERIFIED"
        kind = item["kind"]
        rows.append(
            {
                "order": item["order"],
                "title": item["title"],
                "preserved_status": status,
                "kind": kind,
                "proof_url": gap,
                "proof_url_present": True,
                "proof_controls_display": False,
                "evidence_verdict": verdict,
                "wall_display": display_for(verdict),
                "independently_verified": False,
                "software_built": False,
                "clearance_inferred": False,
                "label_note": (
                    "Preserved Built label. Not a software build and not freshly verified."
                    if kind == "legal_or_certificate_label"
                    else "Preserved board label. Evidence verdict is UNVERIFIED."
                ),
            }
        )
    green = sum(1 for row in rows if row["wall_display"] == "green")
    return {
        "prototype": "NEW-MINIMAL-PROTOTYPE-NOT-ORIGINAL",
        "original_executable": "NOT_LOCATED",
        "fixture_kind": raw["fixture_kind"],
        "audit_label": raw["audit_label"],
        "audit_timestamp": raw["audit_timestamp"],
        "notion_connected": False,
        "proof_url_meaning": raw["proof_url_meaning"],
        "gap_matrix_url": gap,
        "rows": rows,
        "preserved_counts": preserved,
        "declared_counts": raw["preserved_counts"],
        "green_walls": green,
        "treasury": {
            "opening_balance": "UNKNOWN",
            "displayed_as_zero": False,
            "source": "missing — fixture does not invent an amount",
        },
        "popularity": "UNKNOWN",
        "workforce": "UNKNOWN",
        "effects": {
            "permissions": "none",
            "financial_actions": "none",
            "filings": "none",
        },
    }


class Store:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(path.parent, 0o700)
        self.path = path
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self._init()
        self.guest_book = hosted_preview.GuestBook(self.conn, self.lock, path.parent)

    def _init(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
              k TEXT PRIMARY KEY,
              v TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS records (
              id TEXT PRIMARY KEY,
              site_label TEXT NOT NULL,
              purpose TEXT NOT NULL,
              package_code TEXT NOT NULL,
              status TEXT NOT NULL,
              idempotency_key TEXT NOT NULL UNIQUE,
              correlation_id TEXT NOT NULL UNIQUE,
              note TEXT NOT NULL,
              synthetic INTEGER NOT NULL CHECK (synthetic = 1),
              billing_state TEXT NOT NULL,
              amount_cents INTEGER,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              record_id TEXT,
              kind TEXT NOT NULL,
              dedup_key TEXT UNIQUE,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS score_events (
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              dedup_key TEXT NOT NULL UNIQUE,
              correlation_id TEXT NOT NULL,
              subject TEXT NOT NULL,
              evidence_ref TEXT NOT NULL,
              review_state TEXT NOT NULL,
              points INTEGER,
              synthetic INTEGER NOT NULL,
              note TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        self.conn.execute(
            "INSERT INTO meta(k, v) VALUES('schema', '3') "
            "ON CONFLICT(k) DO UPDATE SET v = excluded.v"
        )
        self.conn.commit()

    def probe(self) -> bool:
        with self.lock:
            now = utcnow()
            self.conn.execute("BEGIN IMMEDIATE")
            self.conn.execute(
                "INSERT INTO meta(k, v) VALUES('health_probe', ?) "
                "ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (now,),
            )
            self.conn.commit()
        return True

    def create_record(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        note = body.get("note") or ""
        canonical = {
            "site_label": body["site_label"],
            "purpose": body["purpose"],
            "package_code": body["package_code"],
            "correlation_id": body["correlation_id"],
            "note": note,
        }
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            existing = self.conn.execute(
                "SELECT * FROM records WHERE idempotency_key = ?",
                (body["idempotency_key"],),
            ).fetchone()
            if existing is not None:
                if self._canonical(existing) != canonical:
                    self.conn.rollback()
                    return 409, {"error": "conflict", "deduped": False}
                self.conn.commit()
                return 200, self._record_payload(existing, deduped=True)
            by_correlation = self.conn.execute(
                "SELECT id FROM records WHERE correlation_id = ?",
                (body["correlation_id"],),
            ).fetchone()
            if by_correlation is not None:
                self.conn.rollback()
                return 409, {"error": "duplicate_correlation", "deduped": False}
            count = self.conn.execute("SELECT COUNT(*) AS n FROM records").fetchone()["n"]
            record_id = "TS-%04d" % (count + 1)
            now = utcnow()
            self.conn.execute(
                """
                INSERT INTO records (
                  id, site_label, purpose, package_code, status,
                  idempotency_key, correlation_id, note, synthetic,
                  billing_state, amount_cents, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'received', ?, ?, ?, 1, 'disabled', NULL, ?, ?)
                """,
                (
                    record_id,
                    body["site_label"],
                    body["purpose"],
                    body["package_code"],
                    body["idempotency_key"],
                    body["correlation_id"],
                    note,
                    now,
                    now,
                ),
            )
            row = self.conn.execute(
                "SELECT * FROM records WHERE id = ?", (record_id,)
            ).fetchone()
            self._append_event(
                record_id,
                "record.created",
                "create:%s" % body["idempotency_key"],
                self._public_record(row),
                now,
            )
            self.conn.commit()
            return 201, self._record_payload(row, deduped=False)

    def _canonical(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "site_label": row["site_label"],
            "purpose": row["purpose"],
            "package_code": row["package_code"],
            "correlation_id": row["correlation_id"],
            "note": row["note"],
        }

    def list_records(self) -> dict[str, Any]:
        with self.lock:
            rows = self.conn.execute(
                "SELECT * FROM records ORDER BY created_at, id"
            ).fetchall()
        return {"records": [self._public_record(row) for row in rows]}

    def get_record(self, record_id: str) -> Optional[dict[str, Any]]:
        with self.lock:
            row = self.conn.execute(
                "SELECT * FROM records WHERE id = ?", (record_id,)
            ).fetchone()
            if row is None:
                return None
            events = self.conn.execute(
                "SELECT seq, kind, dedup_key, payload_json, created_at "
                "FROM events WHERE record_id = ? ORDER BY seq",
                (record_id,),
            ).fetchall()
        payload = self._record_payload(row, deduped=False)
        payload["events"] = [
            {
                "seq": event["seq"],
                "kind": event["kind"],
                "dedup_key": event["dedup_key"],
                "payload": json.loads(event["payload_json"]),
                "created_at": event["created_at"],
            }
            for event in events
        ]
        return payload

    def set_status(self, record_id: str, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        target = body["status"]
        note = body.get("note") or ""
        dedup_key = body.get("dedup_key")
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            row = self.conn.execute(
                "SELECT * FROM records WHERE id = ?", (record_id,)
            ).fetchone()
            if row is None:
                self.conn.rollback()
                return 404, {"error": "not_found"}
            if dedup_key:
                prior = self.conn.execute(
                    "SELECT payload_json FROM events WHERE dedup_key = ?",
                    (dedup_key,),
                ).fetchone()
                if prior is not None:
                    prior_payload = json.loads(prior["payload_json"])
                    expected = {"from": row["status"], "to": target, "note": note}
                    if prior_payload.get("to") == target and prior_payload.get("note") == note:
                        self.conn.commit()
                        fresh = self.conn.execute(
                            "SELECT * FROM records WHERE id = ?", (record_id,)
                        ).fetchone()
                        payload = self._record_payload(fresh, deduped=True)
                        return 200, payload
                    self.conn.rollback()
                    return 409, {"error": "conflict", "reason": "dedup_collision"}
            if target not in TRANSITIONS.get(row["status"], set()):
                self.conn.rollback()
                return 409, {
                    "error": "invalid_transition",
                    "reason": "invalid_transition",
                    "from": row["status"],
                    "to": target,
                }
            now = utcnow()
            self.conn.execute(
                "UPDATE records SET status = ?, updated_at = ? WHERE id = ?",
                (target, now, record_id),
            )
            fresh = self.conn.execute(
                "SELECT * FROM records WHERE id = ?", (record_id,)
            ).fetchone()
            self._append_event(
                record_id,
                "record.status",
                dedup_key,
                {
                    "from": row["status"],
                    "to": target,
                    "note": note,
                    "synthetic": True,
                },
                now,
            )
            self.conn.commit()
            return 200, self._record_payload(fresh, deduped=False)

    def add_score(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        canonical = {
            "correlation_id": body["correlation_id"],
            "subject": body["subject"],
            "evidence_ref": body["evidence_ref"],
            "review_state": body["review_state"],
            "points": body.get("points", None),
            "synthetic": True,
            "note": body.get("note") or "",
        }
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            job = self.conn.execute(
                "SELECT id FROM records WHERE correlation_id = ?",
                (body["correlation_id"],),
            ).fetchone()
            if job is None:
                self.conn.rollback()
                return 400, {"error": "unknown_correlation"}
            existing = self.conn.execute(
                "SELECT * FROM score_events WHERE dedup_key = ?",
                (body["dedup_key"],),
            ).fetchone()
            if existing is not None:
                prior = json.loads(existing["payload_json"])
                if prior != canonical:
                    self.conn.rollback()
                    return 409, {"error": "conflict", "deduped": False}
                self.conn.commit()
                board = self._scoreboard_unlocked()
                board["deduped"] = True
                return 200, board
            now = utcnow()
            self.conn.execute(
                """
                INSERT INTO score_events (
                  dedup_key, correlation_id, subject, evidence_ref, review_state,
                  points, synthetic, note, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    body["dedup_key"],
                    canonical["correlation_id"],
                    canonical["subject"],
                    canonical["evidence_ref"],
                    canonical["review_state"],
                    canonical["points"],
                    1,
                    canonical["note"],
                    json.dumps(canonical, sort_keys=True),
                    now,
                ),
            )
            self.conn.commit()
            board = self._scoreboard_unlocked()
            board["deduped"] = False
            return 201, board

    def scoreboard(self) -> dict[str, Any]:
        with self.lock:
            return self._scoreboard_unlocked()

    def list_events(self) -> list[dict[str, Any]]:
        with self.lock:
            rows = self.conn.execute(
                "SELECT seq, record_id, kind, dedup_key, payload_json, created_at "
                "FROM events ORDER BY seq"
            ).fetchall()
        return [
            {
                "seq": row["seq"],
                "record_id": row["record_id"],
                "kind": row["kind"],
                "dedup_key": row["dedup_key"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def castle_view(self) -> dict[str, Any]:
        """Read the shared job table. Compliance rows stay on the fixture."""
        board = castle_board()
        jobs = self.list_records()["records"]
        scores = self.scoreboard()
        return {
            "prototype": "NEW-MINIMAL-PROTOTYPE-NOT-ORIGINAL",
            "original_executable": "NOT_LOCATED",
            "limitation": "Original Nov 6 executable was not located. This view is a new minimal prototype.",
            "jobs_source": "shared_records_table",
            "separate_job_copy": False,
            "jobs": jobs,
            "score_events": scores["events"],
            "score_event_count": scores["event_count"],
            "points_state": scores["points_state"],
            "synthetic_points_sum": scores["synthetic_points_sum"],
            "compliance": {
                "green_walls": board["green_walls"],
                "preserved_counts": board["preserved_counts"],
                "declared_counts": board["declared_counts"],
                "rows": board["rows"],
                "audit_label": board["audit_label"],
                "audit_timestamp": board["audit_timestamp"],
                "proof_url_meaning": board["proof_url_meaning"],
                "gap_matrix_url": board["gap_matrix_url"],
                "notion_connected": False,
                "proof_is_completion": False,
            },
            "treasury": board["treasury"],
            "popularity": board["popularity"],
            "workforce": board["workforce"],
            "effects": board["effects"],
        }

    def ledger(self) -> dict[str, Any]:
        view = self.castle_view()
        events = self.list_events()
        jobs = [
            {
                "id": job["id"],
                "correlation_id": job["correlation_id"],
                "idempotency_key": job["idempotency_key"],
                "site_label": job["site_label"],
                "purpose": job["purpose"],
                "package_code": job["package_code"],
                "status": job["status"],
                "note": job["note"],
                "synthetic": job["synthetic"],
                "billing_state": job["billing_state"],
                "amount_cents": job["amount_cents"],
                "invoice": job["invoice"],
                "created_at": job["created_at"],
                "updated_at": job["updated_at"],
            }
            for job in view["jobs"]
        ]
        return {
            "schema": "private-sandbox-ledger-1",
            "store": "shared_sqlite",
            "separate_job_copy": False,
            "jobs": jobs,
            "events": events,
            "score_events": view["score_events"],
            "compliance": {
                "green_walls": view["compliance"]["green_walls"],
                "preserved_counts": view["compliance"]["preserved_counts"],
                "proof_is_completion": False,
                "all_evidence_verdicts": "UNVERIFIED",
            },
            "counts": {
                "jobs": len(jobs),
                "history_event_count": len(events),
                "event_kinds": [event["kind"] for event in events],
                "score_event_count": len(view["score_events"]),
                "points_state": view["points_state"],
                "synthetic_points_sum": view["synthetic_points_sum"],
                "green_walls": view["compliance"]["green_walls"],
                "preserved_counts": view["compliance"]["preserved_counts"],
            },
        }

    def close(self) -> None:
        with self.lock:
            self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            self.conn.close()

    def _scoreboard_unlocked(self) -> dict[str, Any]:
        rows = self.conn.execute(
            "SELECT seq, dedup_key, correlation_id, subject, evidence_ref, "
            "review_state, points, synthetic, note, created_at "
            "FROM score_events ORDER BY seq"
        ).fetchall()
        points = [row["points"] for row in rows if row["points"] is not None]
        events = [
            {
                "seq": row["seq"],
                "dedup_key": row["dedup_key"],
                "correlation_id": row["correlation_id"],
                "subject": row["subject"],
                "evidence_ref": row["evidence_ref"],
                "review_state": row["review_state"],
                "points": row["points"],
                "synthetic": bool(row["synthetic"]),
                "note": row["note"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
        if not points:
            state = "uninitialized"
            total = None
        else:
            state = "synthetic_test_only"
            total = int(sum(points))
        return {
            "points_state": state,
            "synthetic_points_sum": total,
            "event_count": len(events),
            "events": events,
            "effects": {
                "permissions": "none",
                "financial_actions": "none",
                "wall_display": "unchanged",
                "note": "Scores cannot grant access, move money, or turn a wall green.",
            },
        }

    def _append_event(
        self,
        record_id: Optional[str],
        kind: str,
        dedup_key: Optional[str],
        payload: dict[str, Any],
        now: str,
    ) -> None:
        self.conn.execute(
            "INSERT INTO events (record_id, kind, dedup_key, payload_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (record_id, kind, dedup_key, json.dumps(payload, sort_keys=True), now),
        )

    def _public_record(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "correlation_id": row["correlation_id"],
            "idempotency_key": row["idempotency_key"],
            "site_label": row["site_label"],
            "purpose": row["purpose"],
            "package_code": row["package_code"],
            "status": row["status"],
            "note": row["note"],
            "synthetic": row["synthetic"] == 1,
            "billing_state": "disabled",
            "amount_cents": None,
            "invoice": None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _record_payload(self, row: sqlite3.Row, deduped: bool) -> dict[str, Any]:
        payload = self._public_record(row)
        payload["deduped"] = deduped
        payload["persisted"] = True
        payload["money_actions"] = False
        return payload


def validate_create(body: dict[str, Any]) -> Optional[dict[str, str]]:
    extra = set(body) - CREATE_KEYS
    if extra:
        return {"body": "only site_label, purpose, package_code, idempotency_key, correlation_id, note, and synthetic are accepted"}
    missing = {
        "site_label",
        "purpose",
        "package_code",
        "idempotency_key",
        "correlation_id",
    } - set(body)
    if missing:
        return {"body": "missing required fields"}
    errors: dict[str, str] = {}
    site = body.get("site_label")
    if not isinstance(site, str) or not SITE_RE.fullmatch(site):
        errors["site_label"] = "use a SYNTHETIC- label; real addresses are rejected"
    purpose = body.get("purpose")
    if purpose not in PURPOSES:
        errors["purpose"] = "unsupported purpose"
    package = body.get("package_code")
    if package not in PACKAGES:
        errors["package_code"] = "unsupported package code"
    request_id = body.get("idempotency_key")
    if not isinstance(request_id, str) or not REQUEST_RE.fullmatch(request_id):
        errors["idempotency_key"] = "use 8-64 letters, digits, underscore, or hyphen"
    correlation = body.get("correlation_id")
    if not isinstance(correlation, str) or not CORR_RE.fullmatch(correlation):
        errors["correlation_id"] = "use a CORR-SYNTHETIC- id"
    note = body.get("note", "")
    if note is None:
        note = ""
    if not isinstance(note, str) or not NOTE_RE.fullmatch(note) or looks_like_identifier(note):
        errors["note"] = "notes cannot contain contact details or addresses"
    if body.get("synthetic") is not True:
        errors["synthetic"] = "this sandbox stores synthetic jobs only"
    for key in ("site_label", "purpose", "package_code", "idempotency_key", "correlation_id"):
        value = body.get(key)
        if isinstance(value, str) and looks_like_identifier(value):
            errors[key] = "identifiers are not accepted"
    return errors or None


def validate_status(body: dict[str, Any]) -> Optional[dict[str, str]]:
    extra = set(body) - STATUS_KEYS
    if extra:
        return {"body": "status, note, and dedup_key are the only accepted fields"}
    status = body.get("status")
    blocked = {"booked", "assigned", "flown", "delivered", "invoiced", "paid", "cancelled"}
    if isinstance(status, str) and status.lower() in blocked:
        return {"status": "job, invoice, and payment statuses are disabled"}
    if status not in STATUSES or status == "received":
        return {"status": "unsupported status"}
    note = body.get("note", "")
    if note is None:
        note = ""
    if not isinstance(note, str) or not NOTE_RE.fullmatch(note) or looks_like_identifier(note):
        return {"note": "notes cannot contain contact details or addresses"}
    if "dedup_key" in body and body["dedup_key"] is not None:
        if not isinstance(body["dedup_key"], str) or not DEDUP_RE.fullmatch(body["dedup_key"]):
            return {"dedup_key": "invalid dedup key"}
    return None


def validate_score(body: dict[str, Any]) -> Optional[dict[str, str]]:
    extra = set(body) - SCORE_KEYS
    if extra:
        return {"body": "unsupported score fields"}
    for key in ("dedup_key", "subject", "evidence_ref", "review_state", "correlation_id"):
        if key not in body:
            return {"body": "missing score fields"}
    if not isinstance(body.get("correlation_id"), str) or not CORR_RE.fullmatch(body["correlation_id"]):
        return {"correlation_id": "use a CORR-SYNTHETIC- id"}
    if not isinstance(body["dedup_key"], str) or not DEDUP_RE.fullmatch(body["dedup_key"]):
        return {"dedup_key": "invalid dedup key"}
    if body["subject"] not in SUBJECTS:
        return {"subject": "unsupported subject"}
    evidence = body["evidence_ref"]
    if not isinstance(evidence, str) or not EVIDENCE_RE.fullmatch(evidence) or "://" in evidence:
        return {"evidence_ref": "use a local evidence ref, not a URL"}
    note = body.get("note", "")
    if note is None:
        note = ""
    if not isinstance(note, str) or not NOTE_RE.fullmatch(note) or looks_like_identifier(note):
        return {"note": "notes cannot contain contact details or addresses"}
    if body.get("synthetic") is not True:
        return {"synthetic": "evidence in this sandbox must be marked synthetic"}
    points = body.get("points", None)
    review = body["review_state"]
    if points is None:
        if review != "uninitialized":
            return {"review_state": "omit points to keep the score uninitialized"}
        return None
    if isinstance(points, bool) or not isinstance(points, int) or isinstance(points, float):
        return {"points": "points must be a whole number or omitted"}
    if points < 0 or points > 100:
        return {"points": "points must be from 0 through 100"}
    if review != "synthetic_recorded":
        return {"points": "points are accepted only on an explicit synthetic test event"}
    return None


def validate_rule(body: dict[str, Any]) -> Optional[dict[str, str]]:
    extra = set(body) - RULE_KEYS
    if extra:
        return {"body": "unsupported rule fields"}
    verdict = body.get("evidence_verdict")
    if verdict not in {"UNVERIFIED", "EXPLICIT_FAIL", "EXPLICIT_PASS", "UNKNOWN"}:
        return {"evidence_verdict": "unsupported verdict"}
    if not isinstance(body.get("proof_url_present"), bool):
        return {"proof_url_present": "expected true or false"}
    if body.get("preserved_status") not in PRESERVED_STATUSES:
        return {"preserved_status": "unsupported preserved status"}
    return None


def load_token(data_dir: Path) -> str:
    env = os.environ.get("SANDBOX_TOKEN")
    if env is not None:
        if len(env) < 16 or len(env) > 200:
            raise SystemExit("SANDBOX_TOKEN must be 16 to 200 characters. The value was not printed.")
        return env
    path = data_dir / "access.token"
    if path.exists():
        token = path.read_text(encoding="utf-8").strip()
        if len(token) < 16:
            raise SystemExit("Existing access file is unusable. Remove it and start again. The value was not printed.")
        os.chmod(path, 0o600)
        print("Using existing local access secret at data/access.token.", file=sys.stderr)
        return token
    token = secrets.token_urlsafe(32)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(token + "\n")
    os.chmod(path, 0o600)
    print(
        "Local access secret written to data/access.token (mode 0600). "
        "Read it on this computer. Do not paste it into chat.",
        file=sys.stderr,
    )
    return token


class SandboxServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    token: str
    store: Store
    ready: bool


class Handler(BaseHTTPRequestHandler):
    server: SandboxServer
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("sandbox %s\n" % (fmt % args))

    def do_GET(self) -> None:
        self._route("GET")

    def do_POST(self) -> None:
        self._route("POST")

    def do_DELETE(self) -> None:
        self._route("DELETE")

    def do_PUT(self) -> None:
        self._send(405, {"error": "method_not_allowed"})

    def do_OPTIONS(self) -> None:
        self._send(403, {"error": "forbidden"})

    def _route(self, method: str) -> None:
        if self.client_address[0] != BIND_HOST:
            self._send(403, {"error": "forbidden"})
            return
        path = unquote(urlparse(self.path).path)
        if path != path.replace("\\", "") or "\x00" in path or ".." in path:
            self._send(400, {"error": "bad_path"})
            return
        if method == "GET" and path == "/health":
            self._health()
            return
        if method == "GET" and path in STATIC_FILES:
            self._static(path)
            return
        if not path.startswith("/api/"):
            self._send(404, {"error": "not_found"})
            return
        if path.startswith("/api/guest"):
            if not getattr(self.server, "hosted", False):
                self._send(404, {"error": "not_found"})
                return
            if not self._origin_ok():
                self._send(403, {"error": "forbidden"})
                return
            hosted_preview.dispatch(self, method, path)
            return
        if not self._origin_ok():
            self._send(403, {"error": "forbidden"})
            return
        if not self._authorized():
            self._send(401, {"error": "unauthorized"})
            return
        if method == "DELETE":
            self._send(405, {"error": "method_not_allowed"})
            return
        if method == "GET" and path == "/api/castle-board":
            self._send(200, castle_board())
            return
        if method == "GET" and path == "/api/castle-view":
            self._send(200, self.server.store.castle_view())
            return
        if method == "GET" and path == "/api/ledger":
            self._send(200, self.server.store.ledger())
            return
        if method == "GET" and path == "/api/test-records":
            self._send(200, self.server.store.list_records())
            return
        if method == "GET" and path == "/api/scoreboard":
            self._send(200, self.server.store.scoreboard())
            return
        match = re.fullmatch(r"/api/test-records/(TS-\d{4,})", path)
        if method == "GET" and match:
            payload = self.server.store.get_record(match.group(1))
            if payload is None:
                self._send(404, {"error": "not_found"})
            else:
                self._send(200, payload)
            return
        if method == "POST" and path == "/api/test-records":
            self._create()
            return
        status_match = re.fullmatch(r"/api/test-records/(TS-\d{4,})/status", path)
        if method == "POST" and status_match:
            self._status(status_match.group(1))
            return
        if method == "POST" and path == "/api/score-events":
            self._score()
            return
        if method == "POST" and path == "/api/display-rule-check":
            self._rule()
            return
        if path == "/api/castle-board":
            self._send(405, {"error": "fixture_is_read_only"})
            return
        self._send(404, {"error": "not_found"})

    def _health(self) -> None:
        writable = False
        try:
            writable = self.server.store.probe()
        except sqlite3.Error:
            writable = False
        port = self.server.server_address[1]
        self._send(
            200,
            {
                "ok": writable and self.server.ready,
                "ready": writable and self.server.ready,
                "bind": BIND_HOST,
                "port": port,
                "mode": "private-test",
                "live_intake_enabled": LIVE_INTAKE_ENABLED,
                "money_actions": MONEY_ACTIONS,
                "public_listen": False,
                "store": "sqlite",
                "store_writable": writable,
                "account": ACCOUNT,
                "original_stronghold_executable": "NOT_LOCATED",
                "castle_prototype": "NEW-MINIMAL-PROTOTYPE-NOT-ORIGINAL",
                "notion_connected": False,
                "base44": False,
                "hosted": bool(getattr(self.server, "hosted", False)),
                "public_bind_enabled": False,
            },
        )

    def _create(self) -> None:
        body, error = self._json_body()
        if error is not None:
            self._send(error, {"error": "invalid_json" if error == 400 else "rejected"})
            return
        assert body is not None
        errors = validate_create(body)
        if errors:
            self._send(400, {"error": "validation_failed", "fields": errors})
            return
        status, payload = self.server.store.create_record(body)
        self._send(status, payload)

    def _status(self, record_id: str) -> None:
        body, error = self._json_body()
        if error is not None:
            self._send(error, {"error": "invalid_json" if error == 400 else "rejected"})
            return
        assert body is not None
        errors = validate_status(body)
        if errors:
            self._send(400, {"error": "validation_failed", "fields": errors})
            return
        status, payload = self.server.store.set_status(record_id, body)
        self._send(status, payload)

    def _score(self) -> None:
        body, error = self._json_body()
        if error is not None:
            self._send(error, {"error": "invalid_json" if error == 400 else "rejected"})
            return
        assert body is not None
        errors = validate_score(body)
        if errors:
            self._send(400, {"error": "validation_failed", "fields": errors})
            return
        status, payload = self.server.store.add_score(body)
        self._send(status, payload)

    def _rule(self) -> None:
        body, error = self._json_body()
        if error is not None:
            self._send(error, {"error": "invalid_json" if error == 400 else "rejected"})
            return
        assert body is not None
        errors = validate_rule(body)
        if errors:
            self._send(400, {"error": "validation_failed", "fields": errors})
            return
        before = castle_board()
        verdict = str(body["evidence_verdict"])
        wall = display_for(verdict)
        after = castle_board()
        self._send(
            200,
            {
                "preview_only": True,
                "persisted": False,
                "fixture_changed": before != after,
                "evidence_verdict": verdict,
                "proof_url_present": body["proof_url_present"],
                "preserved_status": body["preserved_status"],
                "wall_display": wall,
                "proof_controlled_the_color": False,
                "preserved_status_controlled_the_color": False,
                "green_walls_on_fixture": after["green_walls"],
                "note": "Synthetic preview. The 19 preserved rows were not changed.",
            },
        )

    def _authorized(self) -> bool:
        header = self.headers.get("Authorization") or ""
        presented = header[7:] if header.startswith("Bearer ") else ""
        account = self.headers.get("X-Sandbox-Account") or ""
        token_ok = same_secret(presented, self.server.token)
        account_ok = same_secret(account, ACCOUNT)
        return token_ok and account_ok

    def _origin_ok(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        port = self.server.server_address[1]
        return origin in {
            "http://127.0.0.1:%s" % port,
            "http://localhost:%s" % port,
        }

    def _json_body(self) -> tuple[Optional[dict[str, Any]], Optional[int]]:
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            return None, 400
        if length <= 0 or length > MAX_BODY:
            return None, 413 if length > MAX_BODY else 400
        ctype = self.headers.get("Content-Type") or ""
        if "application/json" not in ctype:
            return None, 415
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None, 400
        if not isinstance(data, dict):
            return None, 400
        return data, None

    def _static(self, path: str) -> None:
        name, content_type = STATIC_FILES[path]
        file_path = (STATIC / name).resolve()
        if STATIC.resolve() not in file_path.parents:
            self._send(404, {"error": "not_found"})
            return
        if not file_path.is_file():
            self._send(404, {"error": "not_found"})
            return
        body = file_path.read_bytes()
        self._bytes(200, body, content_type)

    def _send(
        self,
        status: int,
        payload: dict[str, Any],
        extra_headers: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self._bytes(status, body, "application/json; charset=utf-8", extra_headers)

    def _bytes(
        self,
        status: int,
        body: bytes,
        content_type: str,
        extra_headers: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for name, value in extra_headers or []:
            self.send_header(name, value)
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self'; connect-src 'self'; base-uri 'none'; "
            "form-action 'none'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(body)


def serve() -> None:
    requested = os.environ.get("SANDBOX_BIND", BIND_HOST)
    if requested != BIND_HOST:
        raise SystemExit(
            "Refusing to listen on %s. Public bind is not enabled. "
            "Hosted mode in this stage stays on 127.0.0.1." % requested
        )
    data_dir = Path(os.environ.get("SANDBOX_DATA_DIR", str(ROOT / "data"))).resolve()
    try:
        port = int(os.environ.get("SANDBOX_PORT", "8765"))
    except ValueError:
        raise SystemExit("SANDBOX_PORT must be an integer.")
    if port < 0 or port > 65535:
        raise SystemExit("SANDBOX_PORT is out of range.")
    load_fixture()
    token = load_token(data_dir)
    store = Store(data_dir / "sandbox.sqlite")
    server = SandboxServer((BIND_HOST, port), Handler)
    if server.server_address[0] != BIND_HOST:
        server.server_close()
        raise SystemExit("Refusing a non-loopback socket.")
    server.token = token
    server.store = store
    server.guest_book = store.guest_book
    server.hosted = hosted_preview.hosted_enabled()
    server.ready = True
    actual_port = server.server_address[1]
    listen_path = data_dir / "listen.json"
    listen_path.write_text(
        json.dumps(
            {"host": BIND_HOST, "port": actual_port, "pid": os.getpid()},
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    os.chmod(listen_path, 0o600)
    print(
        "private-test bind=%s:%s live_intake=false money_actions=false "
        "public_listen=false hosted=%s account=%s secret_file=data/access.token "
        "original_stronghold=NOT_LOCATED"
        % (BIND_HOST, actual_port, str(server.hosted).lower(), ACCOUNT),
        file=sys.stderr,
    )

    def stop(signum: int, _frame: Any) -> None:
        server.ready = False
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        server.serve_forever()
    finally:
        server.ready = False
        server.store.close()
        server.server_close()


if __name__ == "__main__":
    try:
        serve()
    except KeyboardInterrupt:
        sys.exit(0)
