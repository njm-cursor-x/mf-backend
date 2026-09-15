# Cursor cloud-agent refresh (do not use for Fandango)

Cursor cloud IPs are blocked by Fandango/Akamai. The live fetch path is a **GrokBot** using the Fandango UI. See [grokbot-refresh.md](grokbot-refresh.md).

This file is only for reloading a snapshot file into a local DB or Railway after a GrokBot (or a human) already wrote JSON:

```bash
python -m ingest.refresh --source file --from-file data/snapshots/YYYY-MM-DD.json --post-url https://<railway-host>
```

Do not run `--source fandango` from a Cursor cloud agent. It will 403 and never see the page.
