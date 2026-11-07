# Security boundaries

This is a single-process local prototype. It is not a security product, and it does not watch anything after the process stops.

## What the process does

- Default ingress is loopback. It listens on `127.0.0.1` only, rejects any other `SANDBOX_BIND`, and rejects a TCP client whose address is not `127.0.0.1`.
- On loopback, a browser `Origin` must be `http://127.0.0.1:<port>` or `http://localhost:<port>`. A missing `Origin` is allowed for non-browser clients.
- Trusted-proxy mode is off unless `SANDBOX_HOSTED=1`, `SANDBOX_INGRESS=trusted-proxy`, an `https` origin with no path, and a proxy secret of at least 24 characters are all set. Incomplete settings exit. In that mode a request is refused unless the proxy secret matches and `X-Forwarded-Proto` is `https`. `X-Forwarded-For` is not trusted. A present `Origin` must equal the configured https origin. The guest cookie then includes `Secure`. This VM's proof does not listen on `0.0.0.0`. The hosted candidate stays FAIL.
- Requires header `Authorization: Bearer <local secret>` and header `X-Sandbox-Account: sandbox-operator` on operator `/api/` routes. Missing, wrong, or mismatched values get the same `401` body.
- Keeps the operator secret in `data/access.token` at mode `0600`, or in the `SANDBOX_TOKEN` environment of a test process. The server does not print it. The pages do not contain it. The operator API does not use a cookie. After a restart the file is still valid, and the caller must send it again.
- When `SANDBOX_HOSTED=1`, guest jobs are a separate table. A guest code is stored only as a hash. The one-time file `guests/<id>.once` is mode `0600` and is not returned in JSON. `POST /api/guest-session` sets an `HttpOnly` `SameSite=Strict` cookie. On loopback that cookie omits `Secure` because the page is `http://127.0.0.1`. Cookie changes also require `X-Sandbox-Client: guest`. Eight failed direct `Guest` header attempts in ten minutes return `429`.
- Stores jobs in a local SQLite file. The operator secret is not in that file. `/health` runs `SELECT 1` and does not write a probe row.
- Rejects address-like labels, contact details, price fields, invoice routes, and payment statuses. Guest notes must be one of a short allowlist. The same guest idempotency key with a different body returns `409`.
- Leaves billing disabled and the amount NULL.
- Keeps score points from granting access, changing a wall, or creating a money action.
- Serves the preview and guest shell from `static/`: `index.html`, `app.js`, `app.css`, `guest.html`, `guest.js`, and `guest.css`, plus `/health`. Those pages do not list jobs. Every other `/api/` route stays authenticated, except guest session login. In trusted-proxy mode those shells still require the proxy secret.

## What it does not do

- The checks in this package do not bind a public interface, open a tunnel, or call Notion, Dropbox, Stripe, Monday, GitHub, Base44, or email. A fully set trusted-proxy configuration is the only path that names `0.0.0.0`, and this VM did not listen on it.
- It does not store bank data, certificate numbers, or a real client record.
- It does not delete stored events. `DELETE` is rejected.
- It does not turn the 19 fixture rows green.

A person who can read the secret file, or who can reach the port through an SSH tunnel they already control, can call the API. That is local file access, not a remote account system.
