# 07 - DFIR Toolkit

Collect forensic artefacts from demo logs and build an investigation timeline.

## What it does

- Parses a demo event log (`data/sample_events.csv`) with timestamp,
  host, user, event type, and details
- Normalises timestamps to UTC and sorts events into a timeline
- Flags suspicious patterns: logons outside business hours, multiple
  failed logons, a new process spawning from a temp folder, and a large
  outbound transfer after a logon
- Writes `output/timeline.json` and a readable `output/timeline.md`,
  plus a one-page summary of flagged events

## Safety rules

- **Demo data only.** The sample log is invented. This tool reads a CSV
  you point it at; it does not collect artefacts from a live machine,
  does not touch the registry, memory, or disk images, and does not
  run any attack code.
- A real DFIR run would add disk-image parsing, memory analysis, and
  chain-of-custody hashing. Those are listed as extensions in
  `docs/architecture.md`, not implemented here.

## What an employer sees

Log normalisation, timeline building, rule-based flagging with a clear
reason per flag, and a report an investigator can actually read.

## How to run

```bash
cd 07-dfir-toolkit
python3 dfir.py
# or: python3 dfir.py --input data/sample_events.csv --output output/timeline.json
```

Requires Python 3.10+. No dependencies, standard library only.

## Files

- `dfir.py` - CLI: parse, sort, flag, report
- `data/sample_events.csv` - 12 invented demo events
- `docs/architecture.md` - design notes
