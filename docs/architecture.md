# Architecture - DFIR Toolkit

## Pipeline

```
sample_events.csv
  -> dfir.parse_events()   ISO timestamps to UTC, sort chronologically
  -> dfir.flag_events()    rule-based flags, each with a reason
  -> main                  output/timeline.json + output/timeline.md
```

## Design decisions

- **Timeline first.** An investigation starts with "what happened, in
  what order". Sorting and normalising timestamps is the core job;
  flagging is secondary.
- **Every flag explains itself.** Each flag carries a `reason` string
  (e.g. "Failed logon #3 for bob"), so an investigator can check it
  without reading the code.
- **Rules are simple and visible.** Business-hours logon, 3+ failed
  logons, process from a temp folder, outbound transfer >= 100 MB.
  A production tool would tune these per environment; here they are
  documented constants in `dfir.py`.
- **No live collection.** This starter reads a CSV. Real artefact
  collection (disk images, memory, registry, event logs) needs
  chain-of-custody handling and is out of scope for a portfolio starter.

## What to extend next

1. Add SHA-256 hashing of the input file and store it in the report
   (chain of custody).
2. Add parsers for Windows EVTX and Linux auth.log formats.
3. Add a timeline visualisation (HTML page generated from timeline.json).
