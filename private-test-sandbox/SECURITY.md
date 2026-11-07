# Security boundaries

This is a single-process local prototype. It is not a security product, and it does not watch anything after the process stops.

## What the process does

- Listens on `127.0.0.1` only. Any other `SANDBOX_BIND` value exits before listen.
- Rejects a TCP client whose address is not `127.0.0.1`.
- Rejects browser `Origin` values other than `http://127.0.0.1:<port>` and `http://localhost:<port>`.
- Requires header `Authorization: Bearer <local secret>` and header `X-Sandbox-Account: sandbox-operator` on `/api/` routes. Missing, wrong, or mismatched values get the same `401` body.
- Keeps the secret in `data/access.token` at mode `0600`, or in the `SANDBOX_TOKEN` environment of a test process. The server does not print it. The pages do not contain it.
- Uses no cookie. After a restart the file is still valid, and the caller must send it again.
- Stores jobs in a local SQLite file. The secret is not in that file.
- Rejects address-like labels, contact details, price fields, invoice routes, and payment statuses.
- Leaves billing disabled and the amount NULL.
- Keeps score points from granting access, changing a wall, or creating a money action.
- Serves only `index.html`, `app.js`, and `app.css` from `static/`.

## What it does not do

- It does not bind a public interface, open a tunnel, or call Notion, Dropbox, Stripe, Monday, GitHub, Base44, or email.
- It does not store bank data, certificate numbers, or a real client record.
- It does not delete stored events. `DELETE` is rejected.
- It does not turn the 19 fixture rows green.

A person who can read the secret file, or who can reach the port through an SSH tunnel they already control, can call the API. That is local file access, not a remote account system.
