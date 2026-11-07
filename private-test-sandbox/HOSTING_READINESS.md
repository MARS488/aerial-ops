# Hosting readiness — not purchased, not deployed

No account was created. No card was entered. No service was provisioned. No public URL exists. This file is a plan and a disabled rehearsal, not a launch.

The price figures below are from the November 7, 2026 primary-source note that checked Render's public pricing, web-service, disk, bandwidth, FAQ, and build-pipeline pages. This session did not open a Render checkout and did not re-fetch those pages. Tax was not calculated. The parent has been shown the candidate price and has not approved a purchase.

## Candidate price, if a later approval chooses Render

| Piece | Published base |
| --- | --- |
| Hobby workspace, one operator console seat | $0 |
| Starter Python service, 0.5 CPU / 512 MB | $7 / month |
| 1 GB persistent disk | $0.25 / month |
| Base before usage and tax | $7.25 / month |

That base is not a bill cap. The same note lists 5 GB included egress then $0.15/GB, and 500 included build minutes then $5 per 1,000 minutes. Compute is billed while the paid service is on, including idle time. Disk snapshots are not a substitute for a SQLite backup. A second Render console seat would leave Hobby and change the price; guests inside the app are not Render seats.

One-line reason to say before any charge: one small disk-backed Python service is the smallest published way to keep fictional SQLite state and offer HTTPS on the provider hostname without buying a domain.

If a later test shows 512 MB is not enough, stop. The next published compute in that note is 1 CPU / 2 GB at $25/month, plus the $0.25 disk, which is $25.25 before usage and tax. Do not upgrade silently.

## What this session measured

One local Python process, after the guest rehearsal, reported `VmRSS` of about 25 MB. The SQLite file was about 90 KB. That is headroom against a 512 MB label for this tiny workload on this VM. It is not a test inside a 512 MB cgroup, not a test with phone and laptop browsers together, and not a test with the provider's TLS proxy. Capacity and isolation on Render are not validated. Do not treat $7.25 as proof that the service will fit.

Do not serve the walkthrough video from that disk. Keep the video with the local artifact.

## What the code does now

Default behavior is unchanged: `127.0.0.1` only, operator secret file, no guest entrance.

`SANDBOX_HOSTED=1` turns on a separate guest entrance and still refuses every bind except `127.0.0.1`. Public bind is not implemented in this stage.

Guests are not the operator. The operator secret is rejected if it is presented as a guest credential. Each guest has a hashed code, an expiry, and revocation that also drops active sessions. Reset replaces the code and drops old sessions. A guest sees only that guest's fictional jobs. Guest rows live in `guest_jobs`, not in the operator `records` table, so this does not rewrite the older operator history. Guest jobs are synthetic, billing stays disabled, and the amount stays null. Cookie sessions are `HttpOnly` and `SameSite=Strict`. A cookie-backed change also requires the header `X-Sandbox-Client: guest`. Writes are limited per minute. The guest code is written to `guests/<id>.once` at mode `0600` and is not returned in the JSON.

`hosted.example.env` is a comment sheet. It contains no secret.

## Backup

Use SQLite's online backup API, then check the copy, then store that copy off the machine. A disk snapshot is not the restore plan. The guest rehearsal copied the database with the backup API and read the guest rows back from the copy. That was on this VM, not on Render, and not an off-service export.

## Still required before any hands-on release

1. The parent approves the live all-in price, including usage and tax, and the one-line reason.
2. Someone provisions the service. This session did not.
3. A phone and a computer open the provider HTTPS name and complete a fictional job without seeing another guest's rows.
4. An off-service backup is restored onto an isolated copy and checked.
5. A separate reviewer signs that hosted check. This file does not.

No invitation should be sent, and no customer should be told the preview accepts work. The 19 sample checks stay unverified. The original castle source is still not located.
