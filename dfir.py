"""DFIR Toolkit - build an investigation timeline from a demo event log.

Reads a CSV with columns: timestamp, host, user, event, details.
Timestamps are ISO 8601. Flags are rule-based and explain themselves.
Demo data only; this tool does not collect from a live machine.
"""
import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def parse_events(path):
    events = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            events.append({**row, "timestamp_dt": ts})
    return sorted(events, key=lambda e: e["timestamp_dt"])


def flag_events(events):
    """Return a list of {timestamp, event, reason} flags."""
    flags = []
    failed = Counter()
    for e in events:
        hour = e["timestamp_dt"].hour
        if e["event"] == "logon" and (hour < 6 or hour >= 22):
            flags.append({**e, "reason": "Logon outside business hours (06:00-22:00 UTC)."})
        if e["event"] == "failed_logon":
            failed[e["user"]] += 1
            if failed[e["user"]] >= 3:
                flags.append({**e, "reason": f"Failed logon #{failed[e['user']]} for {e['user']}."})
        if e["event"] == "process_start" and "temp" in e["details"].lower():
            flags.append({**e, "reason": "Process started from a temp folder."})
        if e["event"] == "outbound_transfer" and "MB" in e["details"]:
            try:
                size = int(e["details"].split("MB")[0].split()[-1])
                if size >= 100:
                    flags.append({**e, "reason": f"Large outbound transfer ({size} MB)."})
            except ValueError:
                pass
    return flags


def main():
    parser = argparse.ArgumentParser(description="Build a DFIR timeline from a demo event log.")
    parser.add_argument("--input", default="data/sample_events.csv")
    parser.add_argument("--output", default="output/timeline.json")
    args = parser.parse_args()

    events = parse_events(args.input)
    flags = flag_events(events)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    serialised = [{k: v for k, v in e.items() if k != "timestamp_dt"} for e in events]
    out.write_text(json.dumps({"events": serialised, "flags": len(flags)}, indent=2))

    lines = ["# DFIR Timeline", "", f"Events: {len(events)} | Flagged: {len(flags)}", ""]
    for e in events:
        mark = " [!]" if any(f["timestamp"] == e["timestamp"] and f["event"] == e["event"] for f in flags) else ""
        lines.append(f"- {e['timestamp']} {e['host']} {e['user']} {e['event']}: {e['details']}{mark}")
    lines += ["", "## Flagged events", ""]
    for f in flags:
        lines.append(f"- {f['timestamp']} {f['user']} {f['event']}: {f['reason']}")
    (out.parent / "timeline.md").write_text("\n".join(lines) + "\n")

    print(f"Events: {len(events)}  Flagged: {len(flags)}  Report: {out} and output/timeline.md")
    for f in flags:
        print(f"  [!] {f['timestamp']} {f['user']} {f['event']}: {f['reason']}")


if __name__ == "__main__":
    main()
