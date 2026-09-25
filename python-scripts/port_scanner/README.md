# port_scanner

A TCP port scanner written in Python using sockets, now with threading.

## What it does

Asks for a target IP and a port range, then scans each port in that range using a pool of worker threads instead of one at a time. Reports which ports are open and which are closed, then prints a summary at the end. If a port's open, it also tries to grab the banner (whatever the service sends back), and saves the full results to a JSON file when it's done.

You can also leave the end port blank to scan a single port instead of a range.

## How it works

- Validates the IP address format (four dot-separated numbers, each 0-255) before scanning
- Validates the port range (1-65535, start <= end) leave the end port blank to scan just one port
- `scan_port(target, port)` handles one port: opens a TCP socket, tries `connect_ex()` (a return value of 0 means open), and grabs a banner if the connection succeeds. It returns a dict describing the result instead of printing or touching shared state directly, so it's safe to call from multiple threads at once
- A `ThreadPoolExecutor` runs `scan_port()` across up to 100 ports simultaneously (`max_workers=100`), instead of scanning one port at a time
- Uses a 0.4s timeout to connect and a 1s timeout to read a banner, so it doesn't hang forever on closed/filtered ports or silent services
- Ctrl+C is caught both while entering input and mid-scan. During a scan, the pool is shut down without waiting for queued ports, so it exits almost instantly instead of waiting for the whole scan to wind down

## How to run

```
python3 port_scanner.py
```
Then follow the prompts for target IP, start port, and end port (leave end port blank for a single-port scan).

## Example

```
target IP: 127.0.0.1
start port: 20
end port: 25
port 20: closed
port 21: closed
port 22: open (SSH-2.0-OpenSSH_9.6p1)
port 23: closed
port 24: closed
port 25: closed

results saved to scan_127.0.0.1_20260916_144400.json
scanned 6 ports
open: [22]
closed: 5 ports
```

## Why I built it

Wanted to actually understand how port scanning works at the socket level instead of just running nmap. First real networking script I wrote.

## About

It's a TCP connect scanner no raw sockets, no SYN scanning, nothing fancy. It tries a full TCP handshake on each port using `connect_ex()`, which is the slowest but most beginner-friendly way to check if a port's open. What changed since the first version: it used to scan one port at a time, sequentially, which made large ranges slow. It's now threaded, so up to 100 ports get checked at once, the same logic, just distributed across a worker pool instead of a single loop.

## Changelog

**v1 — first working pass**
- Bare-bones sequential TCP connect scan
- IP and port range validation
- Just reports open/closed per port, nothing else

**v2 — added banner grabbing and JSON export**
- Grabs the banner from open ports when the service sends one unprompted
- Saves full scan results to a timestamped JSON file

**v3 — this version**
- Threaded scanning with `ThreadPoolExecutor`, noticeably faster on large ranges
- Refactored the per-port scan logic into its own `scan_port()` function that returns a result instead of mutating shared state, which is what made threading possible
- Ctrl+C now exits cleanly instead of dumping a traceback during input, and mid-scan (with a fast shutdown that doesn't wait for queued ports)
- Single-port scanning: leave end port blank to scan just one port instead of typing it twice
- Split the vague port-range error message into specific ones, so it actually tells you what's wrong

## Status

Still not the final version,  more upgrades are coming as I learn more. Next up: verbosity options, and more cleanup passes on the older parts of the script.
