(function () {
  var ACCOUNT = "sandbox-operator";
  var DEMO = {
    name: "DEMO-JOB-001",
    site: "SYNTHETIC-DEMO-JOB-001",
    correlation: "CORR-SYNTHETIC-DEMO-JOB-001",
    key: "idem-demo-job-001"
  };
  var NEXT = {
    received: "in_review",
    in_review: "reviewed",
    reviewed: "closed_test"
  };
  var STATUS_LABEL = {
    received: "Received",
    in_review: "In review",
    reviewed: "Reviewed",
    closed_test: "Fictional test closed"
  };
  var ACTION_LABEL = {
    in_review: "Mark in review",
    reviewed: "Mark reviewed",
    closed_test: "Close fictional test"
  };
  var CHAPTER = {
    received: "The job is saved. Review is the next fictional step.",
    in_review: "The same saved job is on the sample castle.",
    reviewed: "Reviewed is a test step, not a finished gate.",
    closed_test: "The test is closed. Evidence adds no points."
  };
  var NOTE = {
    received: "Saved on this computer. The castle reads this same job.",
    in_review: "In review only changes this fictional step. Checks stay unverified.",
    reviewed: "Reviewed means further along in the test, not a completed gate.",
    closed_test: "The fictional test is closed. Sample checks are still unverified."
  };
  var ORDER = ["received", "in_review", "reviewed", "closed_test"];
  var job = null;
  var board = null;

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
          throw error;
        }
        return data;
      });
    });
  }

  function showClient() {
    document.getElementById("gate").hidden = true;
    document.getElementById("client").hidden = false;
    window.__previewReady = true;
  }

  document.getElementById("unlock").addEventListener("click", function () {
    var value = document.getElementById("token").value;
    if (!value) {
      text("auth-msg", "Enter the local secret.");
      return;
    }
    sessionStorage.setItem("sandboxSecret", value);
    document.getElementById("token").value = "";
    api("/api/test-records").then(function () {
      text("auth-msg", "");
      showClient();
      return refresh();
    }).catch(function () {
      sessionStorage.removeItem("sandboxSecret");
      text("auth-msg", "That secret was not accepted.");
    });
  });

  document.getElementById("create-form").addEventListener("submit", function (event) {
    event.preventDefault();
    var button = document.getElementById("create-job");
    button.disabled = true;
    api("/api/test-records", {
      method: "POST",
      body: {
        correlation_id: DEMO.correlation,
        idempotency_key: DEMO.key,
        site_label: DEMO.site,
        purpose: document.getElementById("purpose").value,
        package_code: document.getElementById("package").value,
        note: "fictional preview job",
        synthetic: true
      }
    }).then(function () {
      return refresh();
    }).catch(function () {
      button.disabled = false;
      text("chapter", "The fictional job was not saved.");
    });
  });

  document.getElementById("advance").addEventListener("click", function () {
    if (!job) return;
    var status = NEXT[job.status];
    if (!status) return;
    api("/api/test-records/" + job.id + "/status", {
      method: "POST",
      body: {
        status: status,
        note: "fictional review step",
        dedup_key: "status-" + job.idempotency_key + "-" + status
      }
    }).then(function () {
      return refresh();
    }).catch(function () {
      text("chapter", "That step was not applied.");
    });
  });

  document.getElementById("show-castle").addEventListener("click", function () {
    text("chapter", "See the same saved job in the castle");
    document.getElementById("castle").scrollIntoView({ behavior: "smooth", block: "start" });
    draw();
  });

  document.getElementById("record-evidence").addEventListener("click", function () {
    if (!job) return;
    api("/api/score-events", {
      method: "POST",
      body: {
        dedup_key: "score-" + job.idempotency_key,
        correlation_id: job.correlation_id,
        subject: "civilitysync-test",
        evidence_ref: "job:" + job.id.toLowerCase(),
        review_state: "uninitialized",
        note: "fictional evidence",
        synthetic: true
      }
    }).then(function (score) {
      var note = document.getElementById("evidence-note");
      note.hidden = false;
      note.textContent = score.points_state === "uninitialized"
        ? "Fictional evidence saved. No points were added. Sample checks stay unverified."
        : "Fictional evidence saved. Sample checks stay unverified.";
      text("chapter", "Evidence remains unverified");
      return refresh();
    }).catch(function () {
      text("chapter", "Fictional evidence was not saved.");
    });
  });

  function refresh() {
    return Promise.all([loadJob(), loadCastle()]);
  }

  function loadJob() {
    return api("/api/test-records").then(function (payload) {
      job = null;
      payload.records.forEach(function (row) {
        if (row.idempotency_key === DEMO.key) job = row;
      });
      var card = document.getElementById("job-card");
      var advance = document.getElementById("advance");
      var evidence = document.getElementById("record-evidence");
      if (!job) {
        card.hidden = true;
        return;
      }
      card.hidden = false;
      document.getElementById("create-job").disabled = true;
      text("job-title", DEMO.name);
      text("job-status", STATUS_LABEL[job.status] || job.status);
      text("job-note", NOTE[job.status] || "This is the same record the sample castle reads.");
      text("chapter", CHAPTER[job.status] || "Save a fictional job so you can follow it.");
      paintRail(job.status);
      var next = NEXT[job.status];
      if (next) {
        advance.hidden = false;
        advance.textContent = ACTION_LABEL[next];
      } else {
        advance.hidden = true;
      }
      evidence.hidden = job.status !== "closed_test";
    });
  }

  function loadCastle() {
    return api("/api/castle-view").then(function (payload) {
      board = payload;
      var match = null;
      payload.jobs.forEach(function (row) {
        if (row.idempotency_key === DEMO.key) match = row;
      });
      text(
        "shared-line",
        match
          ? DEMO.name + " is the saved job. Status: " + (STATUS_LABEL[match.status] || match.status)
          : "No fictional job saved yet"
      );
      text("verified-count", "Verified segments: " + payload.compliance.green_walls);
      draw();
    });
  }

  function paintRail(status) {
    var index = ORDER.indexOf(status);
    document.querySelectorAll("#rail li").forEach(function (item) {
      var step = ORDER.indexOf(item.getAttribute("data-step"));
      var state = "upcoming";
      if (step < index) state = "done";
      if (step === index) state = "current";
      item.setAttribute("data-state", state);
    });
  }

  function fillRound(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
    ctx.fill();
  }

  function draw() {
    var canvas = document.getElementById("yard");
    if (!canvas || !board) return;
    var ctx = canvas.getContext("2d");
    var w = canvas.width;
    var h = canvas.height;
    var rows = board.compliance.rows;
    var match = null;
    board.jobs.forEach(function (row) {
      if (row.idempotency_key === DEMO.key) match = row;
    });
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#e4eef3";
    ctx.fillRect(0, 0, w, 210);
    ctx.fillStyle = "#efe6d6";
    ctx.fillRect(0, 210, w, h - 210);
    ctx.fillStyle = "#8aa0ad";
    fillRound(ctx, 78, 168, w - 156, 150, 28);
    ctx.fillStyle = "#6d675c";
    ctx.fillRect(150, 132, w - 300, 150);
    ctx.fillStyle = "#7a7468";
    for (var notch = 0; notch < 12; notch += 1) {
      ctx.fillRect(168 + notch * 52, 112, 28, 24);
    }
    ctx.fillStyle = "#524d45";
    ctx.fillRect(112, 78, 78, 214);
    ctx.fillRect(w - 190, 78, 78, 214);
    ctx.fillStyle = "#6d675c";
    ctx.fillRect(104, 64, 94, 20);
    ctx.fillRect(w - 198, 64, 94, 20);
    ctx.fillStyle = "#efe6d6";
    ctx.beginPath();
    ctx.arc(w / 2, 214, 34, Math.PI, 0);
    ctx.rect(w / 2 - 34, 214, 68, 68);
    ctx.fill();
    rows.forEach(function (row, index) {
      var x = 176 + index * ((w - 380) / Math.max(rows.length - 1, 1));
      ctx.fillStyle = row.wall_display === "green" ? "#2f6b3c" : "#3e3a34";
      fillRound(ctx, x, 246, 16, 16, 3);
    });
    ctx.fillStyle = "#1a2420";
    ctx.font = "600 22px system-ui, Segoe UI, Helvetica, Arial, sans-serif";
    ctx.fillText("Sample visualization. Not an earlier sketch.", 96, h - 52);
    ctx.font = "20px system-ui, Segoe UI, Helvetica, Arial, sans-serif";
    ctx.fillText(
      match ? (DEMO.name + "  ·  " + (STATUS_LABEL[match.status] || match.status)) : "No fictional job saved yet",
      96,
      h - 24
    );
  }

  window.__previewBound = true;
  window.__previewReady = false;
  if (sessionStorage.getItem("sandboxSecret")) {
    api("/api/test-records").then(function () {
      showClient();
      return refresh();
    }).catch(function () {
      sessionStorage.removeItem("sandboxSecret");
    });
  }
})();
