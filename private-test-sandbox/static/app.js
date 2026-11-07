(function () {
  var ACCOUNT = "sandbox-operator";
  var sharedJob = null;

  function text(id, value) {
    document.getElementById(id).textContent = value;
  }

  function api(path, options) {
    var headers = { "X-Sandbox-Account": ACCOUNT };
    var token = sessionStorage.getItem("sandboxSecret") || "";
    if (token) headers.Authorization = "Bearer " + token;
    var opts = options || {};
    if (opts.body) headers["Content-Type"] = "application/json";
    return fetch(path, {
      method: opts.method || "GET",
      headers: headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined
    }).then(function (res) {
      return res.text().then(function (raw) {
        var data = {};
        if (raw) {
          try { data = JSON.parse(raw); } catch (err) { data = { error: "bad_response" }; }
        }
        if (!res.ok) {
          var error = new Error(data.error || "request_failed");
          error.status = res.status;
          error.data = data;
          throw error;
        }
        return data;
      });
    });
  }

  function showError(id, err) {
    var fields = err.data && err.data.fields ? " " + Object.keys(err.data.fields).join(",") : "";
    text(id, (err.status || "") + " " + err.message + fields);
  }

  function loadHealth() {
    return fetch("/health").then(function (res) { return res.json(); }).then(function (health) {
      text(
        "health",
        "ready=" + health.ready +
        " bind=" + health.bind +
        " public_listen=" + health.public_listen +
        " live_intake=" + health.live_intake_enabled +
        " money_actions=" + health.money_actions +
        " original=" + health.original_stronghold_executable
      );
    }).catch(function () {
      text("health", "Health check failed.");
    });
  }

  function randomKey() {
    var bytes = new Uint8Array(8);
    crypto.getRandomValues(bytes);
    return "web-" + Array.prototype.map.call(bytes, function (b) {
      return b.toString(16).padStart(2, "0");
    }).join("");
  }

  document.querySelector("input[name=idempotency_key]").value = randomKey();

  document.getElementById("unlock").addEventListener("click", function () {
    var value = document.getElementById("token").value;
    if (!value) {
      text("auth-msg", "Enter the local secret.");
      return;
    }
    sessionStorage.setItem("sandboxSecret", value);
    document.getElementById("token").value = "";
    api("/api/test-records").then(function () {
      text("auth-msg", "Secret accepted for this tab.");
      return refresh();
    }).catch(function (err) {
      sessionStorage.removeItem("sandboxSecret");
      text("auth-msg", "Rejected (" + err.status + ").");
    });
  });

  document.querySelectorAll("nav button").forEach(function (button) {
    button.addEventListener("click", function () {
      document.querySelectorAll("nav button").forEach(function (item) {
        item.classList.toggle("on", item === button);
      });
      document.querySelectorAll(".tab").forEach(function (section) {
        section.hidden = section.id !== button.getAttribute("data-tab");
      });
      if (button.getAttribute("data-tab") === "castle") draw();
    });
  });

  document.getElementById("intake-form").addEventListener("submit", function (event) {
    event.preventDefault();
    var form = event.target;
    var body = {
      correlation_id: form.correlation_id.value.trim(),
      idempotency_key: form.idempotency_key.value.trim(),
      site_label: form.site_label.value.trim(),
      purpose: form.purpose.value,
      package_code: form.package_code.value,
      note: form.note.value.trim(),
      synthetic: true
    };
    api("/api/test-records", { method: "POST", body: body }).then(function (row) {
      text("intake-out", JSON.stringify(row, null, 2));
      if (!row.deduped) form.idempotency_key.value = randomKey();
      return refresh();
    }).catch(function (err) { showError("intake-out", err); });
  });

  document.getElementById("reload").addEventListener("click", refresh);

  document.getElementById("rule-go").addEventListener("click", function () {
    api("/api/display-rule-check", {
      method: "POST",
      body: {
        preserved_status: document.getElementById("rule-status").value,
        evidence_verdict: document.getElementById("rule-verdict").value,
        proof_url_present: document.getElementById("rule-proof").checked
      }
    }).then(function (result) {
      text(
        "rule-out",
        "preview wall=" + result.wall_display +
        " fixture_changed=" + result.fixture_changed +
        " green_walls_on_fixture=" + result.green_walls_on_fixture +
        ". " + result.note
      );
      return loadCastle();
    }).catch(function (err) { showError("rule-out", err); });
  });

  document.getElementById("evidence").addEventListener("click", function () {
    if (!sharedJob) {
      text("score-out", "No shared job is stored.");
      return;
    }
    api("/api/score-events", {
      method: "POST",
      body: {
        dedup_key: "score-" + sharedJob.idempotency_key,
        correlation_id: sharedJob.correlation_id,
        subject: "civilitysync-test",
        evidence_ref: "job:" + sharedJob.id.toLowerCase(),
        review_state: "uninitialized",
        note: "synthetic evidence",
        synthetic: true
      }
    }).then(function (board) {
      text("score-out", JSON.stringify(board, null, 2));
      return refresh();
    }).catch(function (err) { showError("score-out", err); });
  });

  function refresh() {
    return Promise.all([loadRecords(), loadCastle(), loadScore()]);
  }

  function loadRecords() {
    return api("/api/test-records").then(function (payload) {
      var box = document.getElementById("records");
      box.replaceChildren();
      sharedJob = payload.records[0] || null;
      payload.records.forEach(function (row) {
        var block = document.createElement("div");
        block.className = "record";
        var heading = document.createElement("strong");
        if (row.id === "TS-0001") heading.id = "job-status";
        heading.textContent = row.id + " " + row.status + " " + row.correlation_id;
        block.appendChild(heading);
        var actions = document.createElement("div");
        var nextStatus = {
          received: ["in_review", "rejected"],
          in_review: ["reviewed", "rejected"],
          reviewed: ["closed_test"],
          closed_test: [],
          rejected: []
        }[row.status] || [];
        nextStatus.forEach(function (status) {
          var button = document.createElement("button");
          button.type = "button";
          button.textContent = status;
          button.addEventListener("click", function () {
            api("/api/test-records/" + row.id + "/status", {
              method: "POST",
              body: {
                status: status,
                note: "synthetic review",
                dedup_key: "status-" + row.idempotency_key + "-" + status
              }
            }).then(function (updated) {
              text("readback", JSON.stringify(updated, null, 2));
              return refresh();
            }).catch(function (err) { showError("readback", err); });
          });
          actions.appendChild(button);
        });
        var read = document.createElement("button");
        read.type = "button";
        read.textContent = "Read back";
        read.addEventListener("click", function () {
          api("/api/test-records/" + row.id).then(function (full) {
            text("readback", JSON.stringify(full, null, 2));
          }).catch(function (err) { showError("readback", err); });
        });
        actions.appendChild(read);
        block.appendChild(actions);
        box.appendChild(block);
      });
      if (!payload.records.length) box.textContent = "No stored jobs.";
    });
  }

  function loadCastle() {
    return api("/api/castle-view").then(function (board) {
      window.__castle = board;
      var job = board.jobs[0];
      text(
        "shared-job",
        job
          ? "Shared job: " + job.id + " status=" + job.status + " correlation=" + job.correlation_id
          : "Shared job: none"
      );
      text("green-count", "Green segments: " + board.compliance.green_walls);
      var counts = board.compliance.preserved_counts;
      text(
        "preserved-counts",
        "Preserved counts: " + counts.Built + " Built, " +
        counts["In progress"] + " In progress, " + counts["Not started"] + " Not started"
      );
      var table = document.createElement("table");
      var head = document.createElement("tr");
      ["Order", "Title", "Preserved status", "Verdict", "Wall"].forEach(function (name) {
        var cell = document.createElement("th");
        cell.textContent = name;
        head.appendChild(cell);
      });
      table.appendChild(head);
      board.compliance.rows.forEach(function (row) {
        var tr = document.createElement("tr");
        tr.className = "board-row " + (row.wall_display === "green" ? "is-green" : "not-green");
        [row.order, row.title, row.preserved_status, row.evidence_verdict, row.wall_display].forEach(function (value) {
          var cell = document.createElement("td");
          cell.textContent = String(value);
          tr.appendChild(cell);
        });
        table.appendChild(tr);
      });
      var host = document.getElementById("board");
      host.replaceChildren(table);
      draw();
    });
  }

  function loadScore() {
    return api("/api/scoreboard").then(function (board) {
      text(
        "points-state",
        "Points state: " + board.points_state +
        " sum=" + board.synthetic_points_sum +
        " events=" + board.event_count
      );
    });
  }

  function draw() {
    var board = window.__castle;
    var canvas = document.getElementById("yard");
    if (!board || !canvas) return;
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#e7e1d2";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#8aa0ad";
    ctx.fillRect(36, 28, 648, 264);
    ctx.fillStyle = "#ddd6c6";
    ctx.fillRect(70, 58, 580, 204);
    board.compliance.rows.forEach(function (row, index) {
      var x = 84 + (index % 10) * 56;
      var y = 74 + Math.floor(index / 10) * 36;
      ctx.fillStyle = row.wall_display === "green" ? "#2f6b3c" : "#6e685c";
      ctx.fillRect(x, y, 40, 22);
      if (row.preserved_status === "Built") {
        ctx.fillStyle = "#f7f4ea";
        ctx.font = "12px sans-serif";
        ctx.fillText("B", x + 16, y + 15);
      }
    });
    ctx.fillStyle = "#1e2922";
    ctx.font = "15px Georgia, serif";
    ctx.fillText("NEW PROTOTYPE — NOT THE NOV 6 SKETCH", 84, 176);
    var job = board.jobs[0];
    ctx.fillText(job ? ("Shared job " + job.id + " " + job.status) : "No synthetic job stored", 84, 202);
    ctx.fillText("Green segments: " + board.compliance.green_walls, 84, 228);
    ctx.fillText("Treasury: " + board.treasury.opening_balance, 84, 252);
  }

  loadHealth();
  window.__sandboxReady = true;
})();
