(function () {
  function text(id, value) {
    document.getElementById(id).textContent = value;
  }

  fetch("/health").then(function (res) { return res.json(); }).then(function (health) {
    if (!health.hosted || health.public_bind_enabled) {
      text("gate-note", "This entrance is off. The preview stays on this computer until a later approved stage.");
      return;
    }
    text("gate-note", "Use the personal code issued for you. It is not the operator secret.");
    document.getElementById("enter").hidden = false;
  }).catch(function () {
    text("gate-note", "This entrance is off.");
  });

  document.getElementById("enter").addEventListener("submit", function (event) {
    event.preventDefault();
    var guestId = document.getElementById("guest-id").value.trim();
    var secret = document.getElementById("guest-code").value;
    document.getElementById("guest-code").value = "";
    fetch("/api/guest-session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ guest_id: guestId, secret: secret })
    }).then(function (res) {
      if (!res.ok) {
        text("enter-msg", "That code was not accepted.");
        return;
      }
      document.getElementById("enter").hidden = true;
      document.getElementById("work").hidden = false;
      return loadJobs();
    }).catch(function () {
      text("enter-msg", "That code was not accepted.");
    });
  });

  document.getElementById("make").addEventListener("submit", function (event) {
    event.preventDefault();
    var bytes = new Uint8Array(6);
    crypto.getRandomValues(bytes);
    var suffix = Array.prototype.map.call(bytes, function (b) {
      return b.toString(16).padStart(2, "0");
    }).join("");
    fetch("/api/guest-jobs", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-Sandbox-Client": "guest"
      },
      body: JSON.stringify({
        site_label: document.getElementById("site").value.trim(),
        purpose: "general_assessment",
        package_code: "quick_look",
        idempotency_key: "guest-" + suffix,
        correlation_id: "CORR-SYNTHETIC-GUEST-" + suffix.toUpperCase(),
        note: "fictional guest job",
        synthetic: true
      })
    }).then(function (res) {
      if (!res.ok) return;
      return loadJobs();
    });
  });

  function loadJobs() {
    return fetch("/api/guest-jobs", { credentials: "same-origin" }).then(function (res) {
      if (!res.ok) return;
      return res.json();
    }).then(function (payload) {
      if (!payload) return;
      var lines = payload.jobs.map(function (job) {
        return job.id + " " + job.status;
      });
      text("job-list", lines.length ? lines.join(", ") : "None yet.");
    });
  }
})();
