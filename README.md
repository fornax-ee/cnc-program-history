# CNC Program History with Git

Collect CNC programs and machine files from shop-floor machines into Git, read-only, so every change has a history: what changed, when, on which machine.

## The problem

In a typical woodworking or metalworking plant:

- programs live on the machine PC, on a USB stick, and in someone's folder, and nobody knows which copy is current;
- an operator edits a program at the machine to fix a problem, and the fix is lost when the PC is replaced;
- a part comes out wrong and nobody can tell what changed since last week;
- machine PCs run old Windows versions and vendor software that IT cannot patch or touch.

## The approach

```
 machine PC (share, read-only)  ─┐
 machine PC (share, read-only)  ─┼─► collector (OT network) ─► Git repo per machine ─► remote (history, diff, search)
 machine PC (share, read-only)  ─┘        │
                                          └─ scan log, errors, alerts
```

- **Read-only, always.** The collector never writes to a machine. A read-only service account and a read-only mount enforce it.
- **One repo (or folder) per machine,** so history and permissions follow the machine.
- **Commit only on change.** Compare content hashes; unchanged files create no commits.
- **Commit metadata** carries machine, scan time and source path, so `git log` answers "when did this change on machine X?".
- **Text formats diff nicely.** Many woodworking CNC formats are text (e.g. woodWOP `.mpr`, Biesse `.cix`/`.bpp`, SCM Xilog `.xxl`), so Git shows exact line changes. Binary or zipped formats are stored as-is and still get a change history.

## Contents

| File | What it covers |
|---|---|
| [docs/design.md](docs/design.md) | Design decisions: access, security, old SMB versions, scheduling, what not to collect |
| [collector/collect.py](collector/collect.py) | Minimal collector: walk a mounted share, copy changed files, commit |
| [collector/machines.example.yaml](collector/machines.example.yaml) | Example machine list |

## What this is not

Not a DNC system that sends programs to machines. It only observes. Sending programs back is a separate, much riskier step that needs its own controls.

## License

MIT (code), CC BY 4.0 (docs).


Drafted with AI assistance, based on hands-on experience

More notes and contact: [fornax.ee](https://www.fornax.ee) · Have a similar problem? Write to info@fornax.ee — happy to help.
