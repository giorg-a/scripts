# port_scanner

A basic TCP port scanner written in Python using sockets.

## What it does

Asks for a target IP and a port range, then tries to connect to each port in that range one by one. Reports which ports are open and which are closed, then prints a summary at the end. If a port's open, it also tries to grab the banner (whatever the service sends back), and saves the full results to a JSON file when it's done.

## How it works

- Validates the IP address format (four dot-separated numbers, each 0-255) before scanning
- Validates the port range (1-65535, start <= end)
- For each port, opens a TCP socket and tries `connect_ex()` — a return value of 0 means the port is open
- Uses a 0.4s timeout per port so it doesn't hang forever on closed/filtered ports

## How to run

```
python3 port_scanner.py
```
Then follow the prompts for target IP, start port, and end port.

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

It's a straightforward TCP connect scanner — no raw sockets, no SYN scanning, nothing fancy. It just tries a full TCP handshake on each port one at a time using `connect_ex()`, which is the slowest but most beginner-friendly way to check if a port's open. It's single-threaded right now, so scanning a big range takes a while — that's one of the first things I want to improve.

## Status

This isn't the final version — it's a first working pass, and I'll keep evolving it as I learn more. Just added banner grabbing and JSON export.
