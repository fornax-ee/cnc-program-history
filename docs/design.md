# Design decisions

## Access

- Each machine PC shares only the program folder(s), read-only, to one service account.
- The collector runs **inside the OT network** (a VM or container on the production platform), not in the office network. Machine PCs never need a route to the office.
- Mount shares read-only on the collector host (`mount -t cifs -o ro,...`). Defense in depth: even a bug in the collector cannot change a program.

## Old SMB versions

Older machine PCs may only speak SMB1. Do not enable SMB1 company-wide for this.

- Find out per machine which SMB version works (test SMB2/3 first).
- If a machine truly needs SMB1, enable it only on the collector host's mount for that one machine (`vers=1.0`), keep that machine in an isolated network segment, and record the exception with a compensating control in the system register.
- Plan to replace or upgrade the machine PC; record the date.

## Scheduling

- Scan every 5–15 minutes, or nightly for machines that rarely change.
- A machine that is switched off is not an error. Log "unreachable" and retry next cycle; alert only after N consecutive failures during working hours.

## What to collect

- Programs, tool tables, machine parameter exports, post-processor configs.
- **Not** operating system files, logs that grow continuously, or anything with personal data.
- Set a file size limit (machine programs are usually far below 10 MB); log and skip larger files.

## Commits

- One commit per scan per machine, containing all changed files.
- Message: `<machine>: <n> files changed (scan <timestamp>)`.
- Author: the collector service, not a person. Who changed the program at the machine is not known from the share; do not pretend it is.

## Where the history lives

Start with a hosted Git remote (private repositories) if company policy allows it. Move to a self-hosted Git server only if needed. Protect the main branch so history cannot be rewritten.

## Useful next steps

- A small web UI: per machine, latest programs, diff between dates, search by program name.
- Link a program to the order or part number that uses it.
- Alert when a program used in production changes outside working hours.
