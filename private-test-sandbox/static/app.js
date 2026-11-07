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
    received: "Review it",
    in_review: "See the same saved job in the castle",
    reviewed: "Continue the fictional review",
    closed_test: "Evidence remains unverified"
  };
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
      text("chapter", CHAPTER[job.status] || "Create a fictional job");
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

  function draw() {
    var canvas = document.getElementById("yard");
    if (!canvas || !board) return;
    var ctx = canvas.getContext("2d");
    var rows = board.compliance.rows;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#efe8da";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#8aa0ad";
    ctx.fillRect(48, 36, 784, 250);
    ctx.fillStyle = "#e4dccb";
    ctx.fillRect(86, 70, 708, 180);
    rows.forEach(function (row, index) {
      var x = 108 + (index % 10) * 68;
      var y = 92 + Math.floor(index / 10) * 48;
      ctx.fillStyle = row.wall_display === "green" ? "#2f6b3c" : "#6e685c";
      ctx.fillRect(x, y, 48, 26);
    });
    ctx.fillStyle = "#1b2420";
    ctx.font = "22px Georgia, serif";
    ctx.fillText("Sample visualization — not an earlier sketch", 108, 214);
    ctx.font = "18px Georgia, serif";
    var match = null;
    board.jobs.forEach(function (row) {
      if (row.idempotency_key === DEMO.key) match = row;
    });
    ctx.fillText(match ? (DEMO.name + " · " + (STATUS_LABEL[match.status] || match.status)) : "No fictional job saved yet", 108, 244);
    ctx.fillText("Verified segments: " + board.compliance.green_walls, 108, 272);
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
