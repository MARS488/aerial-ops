#!/usr/bin/env python3
"""One synthetic job through Civility and the new castle, on one database.

The script records PASS, FAIL, BLOCKED, or NOT_LOCATED. It does not mark an
independent review as passed. It does not print the access secret.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"
EXPECTED_PATH = Path(__file__).resolve().parent / "expected-counts.json"
ACCOUNT = "sandbox-operator"
JOB_FIELDS = (
    "id",
    "correlation_id",
    "idempotency_key",
    "site_label",
    "purpose",
    "package_code",
    "synthetic",
    "status",
    "note",
    "billing_state",
    "amount_cents",
    "invoice",
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class Client:
    def __init__(self, port: int, secret: str) -> None:
        self.base = "http://127.0.0.1:%s" % port
        self.secret = secret

    def call(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
        token: Optional[str] = "",
        account: Optional[str] = ACCOUNT,
        origin: Optional[str] = None,
        auth: bool = True,
    ) -> tuple[int, dict]:
        data = None
        headers = {}
        if body is not None:
            data = canonical(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if auth:
            headers["Authorization"] = "Bearer " + (self.secret if token == "" else token or "")
            if account is not None:
                headers["X-Sandbox-Account"] = account
        if origin:
            headers["Origin"] = origin
        request = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                raw = response.read().decode("utf-8")
                return response.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                payload = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                payload = {"error": "unreadable"}
            return exc.code, payload


def start_server(data: Path, log_path: Path, bind: str = "127.0.0.1") -> subprocess.Popen:
    env = os.environ.copy()
    env.pop("SANDBOX_TOKEN", None)
    env.pop("SANDBOX_INGRESS", None)
    env.pop("SANDBOX_PUBLIC_ORIGIN", None)
    env.pop("SANDBOX_PROXY_SHARED_SECRET", None)
    env.pop("SANDBOX_HOSTED", None)
    env.pop("PORT", None)
    env["SANDBOX_DATA_DIR"] = str(data)
    env["SANDBOX_PORT"] = "0"
    env["SANDBOX_BIND"] = bind
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handle = log_path.open("a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=str(ROOT),
        env=env,
        stdout=handle,
        stderr=subprocess.STDOUT,
    )
    proc._log_handle = handle  # type: ignore[attr-defined]
    return proc


def stop_server(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        proc.send_signal(15)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
    handle = getattr(proc, "_log_handle", None)
    if handle is not None:
        handle.close()


def wait_listen(proc: subprocess.Popen, data: Path) -> dict:
    listen = data / "listen.json"
    if listen.exists():
        listen.unlink()
    deadline = time.time() + 8
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("server exited before listening")
        if listen.exists():
            info = json.loads(listen.read_text(encoding="utf-8"))
            if info.get("pid") == proc.pid:
                return info
        time.sleep(0.05)
    raise RuntimeError("listen file missing")


def read_secret(data: Path) -> str:
    path = data / "access.token"
    mode = path.stat().st_mode & 0o777
    if mode != 0o600:
        raise RuntimeError("secret file mode is not 0600")
    secret = path.read_text(encoding="utf-8").strip()
    if len(secret) < 16:
        raise RuntimeError("secret file is unusable")
    return secret


def project(record: dict) -> dict:
    return {key: record.get(key) for key in JOB_FIELDS}


def history_kinds(record: dict) -> list[str]:
    return [event["kind"] for event in record.get("events", [])]


def observed(ledger: dict, record: dict) -> dict:
    job = ledger["jobs"][0]
    return {
        "jobs": ledger["counts"]["jobs"],
        "job_id": job["id"],
        "correlation_id": job["correlation_id"],
        "idempotency_key": job["idempotency_key"],
        "status": job["status"],
        "history_event_count": ledger["counts"]["history_event_count"],
        "event_kinds": ledger["counts"]["event_kinds"],
        "score_event_count": ledger["counts"]["score_event_count"],
        "points_state": ledger["counts"]["points_state"],
        "synthetic_points_sum": ledger["counts"]["synthetic_points_sum"],
        "green_walls": ledger["counts"]["green_walls"],
        "preserved_counts": ledger["counts"]["preserved_counts"],
        "billing_state": job["billing_state"],
        "amount_cents": job["amount_cents"],
        "invoice": job["invoice"],
        "duplicate_jobs_after_replay": ledger["counts"]["jobs"],
        "invalid_stored_jobs": 0 if ledger["counts"]["jobs"] == 1 else ledger["counts"]["jobs"],
        "readback_event_kinds": history_kinds(record),
        "readback_status": record.get("status"),
    }


def sqlite_counts(path: Path) -> dict:
    uri = "file:%s?mode=ro" % path
    conn = sqlite3.connect(uri, uri=True)
    try:
        jobs = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        scores = conn.execute("SELECT COUNT(*) FROM score_events").fetchone()[0]
        billing = conn.execute("SELECT billing_state, amount_cents FROM records").fetchall()
        record_synthetic = [row[0] for row in conn.execute("SELECT synthetic FROM records").fetchall()]
        score_rows = [
            {"synthetic": row[0], "points": row[1]}
            for row in conn.execute("SELECT synthetic, points FROM score_events").fetchall()
        ]
        score_payloads = [
            json.loads(row[0]) for row in conn.execute("SELECT payload_json FROM score_events").fetchall()
        ]
    finally:
        conn.close()
    return {
        "records": jobs,
        "events": events,
        "score_events": scores,
        "billing_rows": [{"billing_state": row[0], "amount_cents": row[1]} for row in billing],
        "record_synthetic": record_synthetic,
        "score_rows": score_rows,
        "score_payloads": score_payloads,
    }


class StageFailure(Exception):
    pass


def listen_is_loopback(port: int) -> bool:
    needle = "%04X" % port
    found = False
    for line in Path("/proc/net/tcp").read_text(encoding="utf-8").splitlines()[1:]:
        local, _remote, state = line.split()[1:4]
        addr, hex_port = local.split(":")
        if hex_port.upper() == needle and state == "0A":
            found = True
            if addr.upper() != "0100007F":
                return False
    return found


def other_ips() -> list[str]:
    try:
        text = subprocess.check_output(["hostname", "-I"], text=True, timeout=2)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [item for item in text.split() if item and not item.startswith("127.")]


def banned_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    banned_roots = {"requests", "httpx", "smtplib", "stripe", "notion"}
    found = []
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
        for name in names:
            root = name.split(".")[0]
            if name.startswith("urllib.request") or name.startswith("urllib.error") or name == "urllib":
                found.append(name)
            elif root in banned_roots:
                found.append(name)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = node.func.value.id if isinstance(node.func.value, ast.Name) else ""
            if node.func.attr == "create_connection" or (
                node.func.attr == "connect" and owner != "sqlite3"
            ):
                found.append(owner + "." + node.func.attr)
    return found


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def write_outputs(out: Path, report: dict, ledger: Optional[dict], db_counts: Optional[dict]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "run-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if ledger is not None:
        (out / "ledger.json").write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if db_counts is not None:
        (out / "db-counts.json").write_text(json.dumps(db_counts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Shared scenario run",
        "",
        "Environment: `%s`" % report["environment"],
        "Mode: `%s`" % report["mode"],
        "Overall: `%s`" % report["overall"],
        "",
        "Browser interaction was not run. SKIPPED_NOT_RUN is not a pass.",
        "Independent review stays PENDING. This process does not sign it.",
        "The environment value comes only from --execution-environment.",
        "",
        "| Stage | Outcome | Detail |",
        "| --- | --- | --- |",
    ]
    for stage in report["stages"]:
        detail = str(stage.get("detail", "")).replace("|", "/")
        lines.append("| %s | %s | %s |" % (stage["stage"], stage["outcome"], detail))
    lines.append("")
    (out / "run-report.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[Path, Optional[str]]:
    """API-only is the only mode. The environment is whatever flag the invoker passes."""
    out = ROOT / "run-output"
    declared = None
    saw_output = False
    saw_environment = False
    index = 1
    while index < len(argv):
        arg = argv[index]
        if arg in {"--api-only", "--skip-browser"}:
            index += 1
            continue
        if arg in {"--with-browser", "--browser", "--capture"}:
            raise SystemExit(
                "This scenario does not start a browser. "
                "Run: python3 tests/shared_e2e_scenario.py --api-only "
                "--execution-environment cloud_vm_loopback --output run-output"
            )
        if arg == "--output":
            if saw_output or index + 1 >= len(argv):
                raise SystemExit("--output needs one directory")
            out = Path(argv[index + 1]).resolve()
            saw_output = True
            index += 2
            continue
        if arg == "--execution-environment":
            if saw_environment or index + 1 >= len(argv):
                raise SystemExit("--execution-environment needs one value")
            declared = argv[index + 1]
            if declared not in {"cloud_vm_loopback", "parent_local"}:
                raise SystemExit(
                    "--execution-environment must be cloud_vm_loopback or parent_local"
                )
            saw_environment = True
            index += 2
            continue
        raise SystemExit(
            "Unknown argument. Supported: --api-only, --skip-browser, "
            "--execution-environment cloud_vm_loopback|parent_local, --output DIR"
        )
    return out, declared


def main() -> int:
    out, declared_environment = parse_args(sys.argv)
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
    if out.exists():
        shutil.rmtree(out)
    data = out / "data"
    data.mkdir(parents=True, exist_ok=True)
    log_path = out / "server.log"
    stages: list[dict[str, str]] = []
    ledger = None
    db_counts = None
    secret = ""

    def add(stage: str, outcome: str, detail: str = "") -> None:
        stages.append({"stage": stage, "outcome": outcome, "detail": detail})

    def fail(stage: str, detail: str) -> None:
        add(stage, "FAIL", detail)
        raise StageFailure()

    try:
        proc = start_server(data, log_path)
        info = wait_listen(proc, data)
        secret = read_secret(data)
        client = Client(info["port"], secret)
        status, health = client.call("GET", "/health", auth=False)
        if status != 200 or health.get("ready") is not True or health.get("public_listen") is not False:
            fail("health", "status=%s ready=%s" % (status, health.get("ready")))
        add("health", "PASS", "ready on 127.0.0.1")

        code, _ = client.call("POST", "/api/test-records", expected_body(expected), auth=False)
        if code != 401:
            fail("auth.missing", "expected 401 got %s" % code)
        add("auth.missing", "PASS", "401")
        code, _ = client.call("GET", "/api/test-records", token="not-the-local-secret", auth=True)
        if code != 401:
            fail("auth.bad_secret", "expected 401 got %s" % code)
        add("auth.bad_secret", "PASS", "401")
        code, _ = client.call("GET", "/api/test-records", account="other-account")
        if code != 401:
            fail("auth.bad_account", "expected 401 got %s" % code)
        add("auth.bad_account", "PASS", "401")
        code, _ = client.call("GET", "/api/ledger", origin="https://evil.example")
        if code != 403:
            fail("origin.rejected", "expected 403 got %s" % code)
        add("origin.rejected", "PASS", "403")

        bad_address = expected_body(expected)
        bad_address["site_label"] = "412 Oak St"
        bad_address["idempotency_key"] = "idem-invalid-address"
        code, payload = client.call("POST", "/api/test-records", bad_address)
        if code != 400 or payload.get("error") != "validation_failed":
            fail("invalid.address", "expected 400 validation got %s" % code)
        add("invalid.address", "PASS", "400")
        priced = expected_body(expected)
        priced["price"] = 1
        priced["idempotency_key"] = "idem-invalid-price"
        code, payload = client.call("POST", "/api/test-records", priced)
        if code != 400:
            fail("invalid.price", "expected 400 got %s" % code)
        add("invalid.price", "PASS", "400")
        mailed = expected_body(expected)
        mailed["note"] = "reach me at test@example.com"
        mailed["idempotency_key"] = "idem-invalid-mail"
        code, _ = client.call("POST", "/api/test-records", mailed)
        if code != 400:
            fail("invalid.identifier", "expected 400 got %s" % code)
        add("invalid.identifier", "PASS", "400")
        nonsynthetic = expected_body(expected)
        nonsynthetic["synthetic"] = False
        nonsynthetic["idempotency_key"] = "idem-not-synthetic"
        nonsynthetic["correlation_id"] = "CORR-SYNTHETIC-NOT-A-JOB"
        code, payload = client.call("POST", "/api/test-records", nonsynthetic)
        if code != 400 or payload.get("error") != "validation_failed":
            fail("synthetic.job_rejected", "expected 400 got %s" % code)
        add("synthetic.job_rejected", "PASS", "400")
        code, listing = client.call("GET", "/api/test-records")
        if code != 200 or listing.get("records"):
            fail("invalid.stored_nothing", "invalid input left a job")
        add("invalid.stored_nothing", "PASS", "jobs=0")

        code, created = client.call("POST", "/api/test-records", expected_body(expected))
        if (
            code != 201
            or created.get("id") != expected["job_id"]
            or created.get("deduped") is not False
            or created.get("synthetic") is not True
        ):
            fail("valid.intake", "expected 201 %s got %s %s" % (expected["job_id"], code, created.get("id")))
        add("valid.intake", "PASS", created["id"])
        code, replay = client.call("POST", "/api/test-records", expected_body(expected))
        if code != 200 or replay.get("deduped") is not True or replay.get("id") != expected["job_id"]:
            fail("replay.intake", "expected deduped 200 got %s" % code)
        code, listing = client.call("GET", "/api/test-records")
        if len(listing.get("records", [])) != 1:
            fail("replay.intake", "job count %s" % len(listing.get("records", [])))
        add("replay.intake", "PASS", "jobs=1")

        code, castle = client.call("GET", "/api/castle-view")
        same = project(castle["jobs"][0]) == project(created)
        if code != 200 or castle.get("separate_job_copy") is not False or not same:
            fail("castle.same_job", "views differed at received")
        if castle["compliance"]["green_walls"] != 0:
            fail("castle.same_job", "green walls changed on intake")
        add("castle.same_job", "PASS", "shared record at received")

        code, reviewed = client.call(
            "POST",
            "/api/test-records/%s/status" % expected["job_id"],
            {
                "status": expected["review_status"],
                "note": expected["review_note"],
                "dedup_key": expected["review_dedup_key"],
            },
        )
        if code != 200 or reviewed.get("status") != "in_review" or reviewed.get("deduped") is not False:
            fail("review.stage", "expected in_review got %s %s" % (code, reviewed.get("status")))
        add("review.stage", "PASS", "in_review")
        code, reviewed_again = client.call(
            "POST",
            "/api/test-records/%s/status" % expected["job_id"],
            {
                "status": expected["review_status"],
                "note": expected["review_note"],
                "dedup_key": expected["review_dedup_key"],
            },
        )
        code_paid, _paid = client.call(
            "POST",
            "/api/test-records/%s/status" % expected["job_id"],
            {"status": "paid", "note": "synthetic review"},
        )
        full_code, full = client.call("GET", "/api/test-records/%s" % expected["job_id"])
        if reviewed_again.get("deduped") is not True or code_paid != 400 or len(full.get("events", [])) != 2:
            fail(
                "replay.review",
                "deduped=%s paid=%s events=%s" % (reviewed_again.get("deduped"), code_paid, len(full.get("events", []))),
            )
        add("replay.review", "PASS", "events=2 paid_rejected")

        code, collided = client.call(
            "POST",
            "/api/test-records/%s/status" % expected["job_id"],
            {
                "status": "reviewed",
                "note": expected["review_note"],
                "dedup_key": expected["status_dedup_keys"]["in_review"],
            },
        )
        _, after_collision = client.call("GET", "/api/test-records/%s" % expected["job_id"])
        if code != 409 or collided.get("error") != "conflict" or len(after_collision.get("events", [])) != 2:
            fail("status.dedup_collision", "expected 409 conflict got %s %s" % (code, collided.get("error")))
        add("status.dedup_collision", "PASS", "409 conflict")

        code, skipped = client.call(
            "POST",
            "/api/test-records/%s/status" % expected["job_id"],
            {
                "status": "closed_test",
                "note": expected["review_note"],
                "dedup_key": "status-idem-synthetic-job-0001-skip",
            },
        )
        if code != 409 or skipped.get("error") != "invalid_transition":
            fail("status.invalid_transition", "expected 409 invalid_transition got %s %s" % (code, skipped.get("error")))
        add("status.invalid_transition", "PASS", "409 invalid_transition")

        for step, event_count in (("reviewed", 3), ("closed_test", 4)):
            body = {
                "status": step,
                "note": expected["review_note"],
                "dedup_key": expected["status_dedup_keys"][step],
            }
            code, moved = client.call("POST", "/api/test-records/%s/status" % expected["job_id"], body)
            code_again, moved_again = client.call("POST", "/api/test-records/%s/status" % expected["job_id"], body)
            _, current = client.call("GET", "/api/test-records/%s" % expected["job_id"])
            if (
                code != 200
                or moved.get("status") != step
                or moved.get("deduped") is not False
                or moved_again.get("deduped") is not True
                or current.get("status") != step
                or len(current.get("events", [])) != event_count
            ):
                fail("status." + step, "status=%s events=%s code=%s" % (current.get("status"), len(current.get("events", [])), code))
            add("status." + step, "PASS", "events=%s" % event_count)

        score_body = {
            "dedup_key": expected["score_dedup_key"],
            "correlation_id": expected["correlation_id"],
            "subject": expected["score_subject"],
            "evidence_ref": expected["score_evidence_ref"],
            "review_state": "uninitialized",
            "note": expected["score_note"],
            "synthetic": True,
        }
        false_score = dict(score_body)
        false_score["synthetic"] = False
        false_score["dedup_key"] = "score-not-synthetic"
        code, rejected_score = client.call("POST", "/api/score-events", false_score)
        omitted = dict(score_body)
        omitted.pop("synthetic")
        omitted["dedup_key"] = "score-omitted-synthetic"
        code_omitted, _omitted_body = client.call("POST", "/api/score-events", omitted)
        if code != 400 or rejected_score.get("error") != "validation_failed" or code_omitted != 400:
            fail("synthetic.rejected", "false=%s omitted=%s" % (code, code_omitted))
        add("synthetic.rejected", "PASS", "400")
        code, scored = client.call("POST", "/api/score-events", score_body)
        code_again, scored_again = client.call("POST", "/api/score-events", score_body)
        stored_score = (scored.get("events") or [{}])[-1]
        if (
            code != 201
            or scored.get("event_count") != 1
            or scored.get("points_state") != "uninitialized"
            or stored_score.get("synthetic") is not True
            or stored_score.get("points") is not None
        ):
            fail("evidence.once", "first score %s synthetic=%s" % (code, stored_score.get("synthetic")))
        if code_again != 200 or scored_again.get("deduped") is not True or scored_again.get("event_count") != 1:
            fail("evidence.once", "replay did not dedupe")
        add("evidence.once", "PASS", "score_events=1 synthetic=true points_uninitialized")

        code, _ = client.call("DELETE", "/api/test-records/%s" % expected["job_id"])
        if code != 405:
            fail("delete.rejected", "expected 405 got %s" % code)
        add("delete.rejected", "PASS", "405")
        code, _ = client.call("POST", "/api/invoices", {"correlation_id": expected["correlation_id"]})
        if code != 404:
            fail("invoice.absent", "expected 404 got %s" % code)
        add("invoice.absent", "PASS", "404")
        code, _ = client.call("POST", "/api/castle-board", {"green": True})
        if code != 405:
            fail("fixture.readonly", "expected 405 got %s" % code)
        add("fixture.readonly", "PASS", "405")

        code, preview = client.call(
            "POST",
            "/api/display-rule-check",
            {
                "preserved_status": "Built",
                "evidence_verdict": "UNVERIFIED",
                "proof_url_present": True,
            },
        )
        code_castle, castle = client.call("GET", "/api/castle-view")
        built = [row for row in castle["compliance"]["rows"] if row["preserved_status"] == "Built"]
        walls_ok = (
            code == 200
            and preview.get("wall_display") == "not_green"
            and preview.get("fixture_changed") is False
            and castle["compliance"]["green_walls"] == 0
            and len(built) == 2
            and all(row["wall_display"] == "not_green" and row["software_built"] is False for row in built)
            and all(row["evidence_verdict"] == "UNVERIFIED" for row in castle["compliance"]["rows"])
            and castle["compliance"]["preserved_counts"] == expected["preserved_counts"]
        )
        if not walls_ok:
            fail("compliance.not_green", "proof URL or Built label changed a wall")
        add("compliance.not_green", "PASS", "green_walls=0 preserved 2/2/15")

        code_list, listing = client.call("GET", "/api/test-records")
        code_castle, castle = client.call("GET", "/api/castle-view")
        code_ledger, ledger = client.call("GET", "/api/ledger")
        code_full, full = client.call("GET", "/api/test-records/%s" % expected["job_id"])
        views_match = project(listing["records"][0]) == project(castle["jobs"][0]) == project(ledger["jobs"][0])
        if not views_match or full["status"] != expected["status"] or history_kinds(full) != expected["event_kinds"]:
            fail("refresh.match", "civility, castle, or ledger diverged")
        if full.get("synthetic") is not True or ledger["jobs"][0].get("synthetic") is not True:
            fail("refresh.match", "job synthetic flag was not true")
        if ledger["score_events"][0].get("synthetic") is not True or ledger["score_events"][0].get("points") is not None:
            fail("refresh.match", "score export was not synthetic or points were set")
        got = observed(ledger, full)
        for key in (
            "jobs",
            "job_id",
            "correlation_id",
            "idempotency_key",
            "status",
            "history_event_count",
            "event_kinds",
            "score_event_count",
            "points_state",
            "synthetic_points_sum",
            "green_walls",
            "preserved_counts",
            "billing_state",
            "amount_cents",
            "invoice",
        ):
            if got[key] != expected[key]:
                fail("counts.match", "%s expected %s got %s" % (key, expected[key], got[key]))
        add("refresh.match", "PASS", "one job, same three reads")
        if not listen_is_loopback(info["port"]):
            fail("bind.loopback", "listen socket was not 127.0.0.1")
        refused = True
        for ip in other_ips():
            probe = socket.socket()
            probe.settimeout(0.4)
            try:
                probe.connect((ip, info["port"]))
                refused = False
            except OSError:
                refused = True
            finally:
                probe.close()
            if not refused:
                fail("bind.loopback", "connected via %s" % ip)
        imports = banned_imports(SERVER)
        if imports:
            fail("network.no_client", "server imports %s" % ",".join(imports))
        add("bind.loopback", "PASS", "127.0.0.1 only")

        stop_server(proc)
        proc = start_server(data, log_path)
        info = wait_listen(proc, data)
        secret_again = read_secret(data)
        if secret_again != secret:
            fail("restart.secret", "secret file changed")
        restarted = Client(info["port"], secret_again)
        code, _ = restarted.call("GET", "/api/ledger", auth=False)
        if code != 401:
            fail("restart.reauth", "expected 401 got %s" % code)
        add("restart.reauth", "PASS", "401 until secret is presented again")
        code, full_again = restarted.call("GET", "/api/test-records/%s" % expected["job_id"])
        code_castle, castle_again = restarted.call("GET", "/api/castle-view")
        code_ledger, ledger = restarted.call("GET", "/api/ledger")
        if (
            full_again.get("status") != expected["status"]
            or full_again.get("synthetic") is not True
            or history_kinds(full_again) != expected["event_kinds"]
            or project(castle_again["jobs"][0]) != project(full_again)
            or ledger["counts"]["jobs"] != 1
            or ledger["counts"]["score_event_count"] != 1
            or ledger["counts"]["green_walls"] != 0
        ):
            fail("restart.readback", "stored job or history changed")
        add("restart.readback", "PASS", "same id, status, history, score, green_walls")
        stop_server(proc)
        db_counts = sqlite_counts(data / "sandbox.sqlite")
        if (
            db_counts["records"] != 1
            or db_counts["events"] != expected["history_event_count"]
            or db_counts["score_events"] != 1
        ):
            fail("sqlite.counts", json.dumps(db_counts, sort_keys=True))
        if db_counts["billing_rows"] != [{"billing_state": "disabled", "amount_cents": None}]:
            fail("sqlite.counts", "billing row changed")
        if db_counts["record_synthetic"] != [1] or db_counts["score_rows"] != [{"synthetic": 1, "points": None}]:
            fail("sqlite.synthetic", "raw synthetic flag was not 1")
        if any(payload.get("synthetic") is not True for payload in db_counts["score_payloads"]):
            fail("sqlite.synthetic", "exported score payload was not synthetic")
        add("sqlite.counts", "PASS", "records=1 events=4 score_events=1 synthetic=1")

        verifier = subprocess.run(
            [sys.executable, str(ROOT / "verify_stronghold.py")],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        if "status=ORIGINAL_SOURCE_NOT_LOCATED" not in verifier.stdout:
            fail("original.lookup", "verifier did not report NOT_LOCATED")
        add("original.lookup", "NOT_LOCATED", "expected; new castle is not the Nov 6 sketch")

        refused_proc = start_server(out / "bind-refusal", out / "bind-refusal.log", bind="0.0.0.0")
        try:
            refused_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            stop_server(refused_proc)
            fail("bind.refusal", "process stayed up on 0.0.0.0")
        if refused_proc.returncode == 0:
            fail("bind.refusal", "exit 0")
        add("bind.refusal", "PASS", "exit %s" % refused_proc.returncode)
        add(
            "browser.capture",
            "SKIPPED_NOT_RUN",
            "api-only; Chrome was not started and UI interaction was not tested",
        )

        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        if secret and secret in log_text:
            fail("log.redaction", "server log contained the secret")
        add("log.redaction", "PASS", "secret not in server log")
        if declared_environment == "parent_local":
            add("parent.local_run", "DECLARED", "invoker passed --execution-environment parent_local")
        elif declared_environment == "cloud_vm_loopback":
            add("parent.local_run", "NOT_RUN", "invoker passed --execution-environment cloud_vm_loopback")
        else:
            add("parent.local_run", "NOT_CLAIMED", "no --execution-environment flag was passed")
        add("independent.review", "PENDING", "this script does not sign a review")
        outcome = 0
    except StageFailure:
        outcome = 1
    except Exception as exc:
        add("harness", "FAIL", "%s: %s" % (type(exc).__name__, exc))
        outcome = 1
    finally:
        if "proc" in locals():
            stop_server(locals()["proc"])
    failed = [stage for stage in stages if stage["outcome"] == "FAIL"]
    if any(stage["outcome"] == "PASS" and stage["stage"] == "browser.capture" for stage in stages):
        failed.append({"stage": "browser.capture", "outcome": "FAIL", "detail": "browser was marked passed"})
    if failed or outcome:
        overall = "FAILED"
    elif declared_environment == "parent_local":
        overall = "LOCAL_API_ONLY_PASSED_BROWSER_SKIPPED_REVIEW_PENDING"
    elif declared_environment == "cloud_vm_loopback":
        overall = "API_ONLY_PASSED_BROWSER_SKIPPED_REVIEW_PENDING"
    else:
        overall = "API_ONLY_PASSED_BROWSER_SKIPPED_ENVIRONMENT_UNDECLARED_REVIEW_PENDING"
    report = {
        "scenario_id": expected["scenario_id"],
        "environment": declared_environment or "unspecified",
        "environment_source": "invocation_flag" if declared_environment else "not_provided",
        "mode": "api-only",
        "browser": "SKIPPED_NOT_RUN",
        "ui_interaction_tested": False,
        "python": sys.version.split()[0],
        "overall": overall,
        "session_model": "bearer secret file survives restart; no cookie session; caller must present the secret again",
        "original_executable": "NOT_LOCATED",
        "castle_prototype": "NEW-MINIMAL-PROTOTYPE-NOT-ORIGINAL",
        "independent_review": "PENDING",
        "commands": [
            "python3 verify_stronghold.py",
            "python3 tests/shared_e2e_scenario.py --api-only --execution-environment %s --output run-output"
            % (declared_environment or "<cloud_vm_loopback|parent_local>"),
        ],
        "stages": stages,
    }
    write_outputs(out, report, ledger, db_counts)
    sums = []
    for path in (
        SERVER,
        Path(__file__).resolve(),
        EXPECTED_PATH,
        ROOT / "fixtures" / "castle_board_fixture.json",
        out / "ledger.json",
        out / "run-report.json",
        data / "sandbox.sqlite",
    ):
        if path.exists():
            sums.append("%s  %s" % (sha256(path), path))
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(overall)
    for stage in stages:
        print("%s %s" % (stage["outcome"], stage["stage"]))
    return 0 if outcome == 0 and not failed else 1


def expected_body(expected: dict) -> dict:
    return {
        "correlation_id": expected["correlation_id"],
        "idempotency_key": expected["idempotency_key"],
        "site_label": expected["site_label"],
        "purpose": expected["purpose"],
        "package_code": expected["package_code"],
        "note": expected["note"],
        "synthetic": True,
    }


if __name__ == "__main__":
    sys.exit(main())
