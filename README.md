# Linux System Audit

A Python CLI that audits the general health of a Linux server, with an
interactive menu to choose which sections to run.

## Sections
CPU & OS · Memory · Disk · Task manager & services · Network · Warnings

## Requirements
- Linux (tested on Debian)
- Python 3.8+
- No external dependencies (only the standard library: `subprocess`)

## Usage
    python3 audit.py

Choose a section by number (1,2,3,4,5,6) `a` for all, `q` to quit.

Some commands (`dmesg`, `ss -p`) show more information when run with `sudo`.

## Roadmap
- [ ] Non-interactive mode with `argparse`
- [ ] Export report to JSON/text file
- [ ] Threshold warnings (e.g. disk above 80%)
