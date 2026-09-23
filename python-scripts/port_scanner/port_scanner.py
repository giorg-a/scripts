import socket
import re
import json
from datetime import datetime


# Lists used to store scan results
total_ports = []
open_ports = []
closed_ports = []


# Ask for a target IP address until a valid-looking address is entered
while True:
    target = input("target IP: ").strip()

    # Check whether the input has four groups of digits separated by dots
    if not re.search(r"^\d+\.\d+\.\d+\.\d+$", target):
        print("invalid IP shape!")
        continue

    # Split the IP address into its four octets
    octets = target.split(".")

    valid = True

    # Check that every octet is within the valid range: 0-255
    for octet in octets:
        if int(octet) > 255:
            valid = False

    if not valid:
        print("octets out of range!")
        continue

    # Exit the loop after the IP passes validation
    break


# Ask for the starting and ending ports
while True:
    try:
        start_port = int(input("start port: "))
        end_port = int(input("end port: "))

    # This runs if the user enters something that is not a number
    except ValueError:
        print("enter only numbers!")
        continue

    # Check that the port range is valid
    # Valid TCP/UDP port numbers range from 1 to 65535.
    # The starting port must also be less than or equal to the ending port.
    if start_port < 1 or start_port > 65535 or end_port < 1 or end_port > 65535 or start_port > end_port:
        print("invalid port range")
        continue

    # Exit the loop after receiving a valid port range
    break


def scan_port(target, port):
    """
    Scans a single port on the target and returns a dict describing
    the result. Does not print or touch any shared/global lists -
    that bookkeeping happens after this returns, so it's safe to
    call this from multiple threads later.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        result = sock.connect_ex((target, port))

        if result == 0:
            banner = "no banner"
            try:
                sock.settimeout(1)  # a bit longer, specifically for reading
                data = sock.recv(1024)
                if data:
                    banner = data.decode(errors="ignore").strip()
            except (socket.timeout, ConnectionResetError, OSError):
                # No banner arrived in time, or the connection was reset -
                # that's fine, keep the default
                pass

            return {"port": port, "status": "open", "banner": banner}
        else:
            return {"port": port, "status": "closed", "banner": None}


# --- TEMPORARY TEST CODE, delete once you trust scan_port() ---
print(scan_port(target, 80))
print(scan_port(target, 9999))
# ----------------------------------------------------------------


# Scan every port from start_port through end_port
# end_port + 1 is used because Python's range() stops before its
# second value.
for port in range(start_port, end_port + 1):
    outcome = scan_port(target, port)

    total_ports.append(outcome["port"])

    if outcome["status"] == "open":
        open_ports.append({"port": outcome["port"], "banner": outcome["banner"]})
        print(f"port {outcome['port']}: open ({outcome['banner']})")
    else:
        closed_ports.append(outcome["port"])
        print(f"port {outcome['port']}: closed")


# Build a dictionary holding everything about this scan
results = {
    "target": target,
    "scan_time": datetime.now().isoformat(),
    "port_range": {"start": start_port, "end": end_port},
    "total_scanned": len(total_ports),
    "open_ports": open_ports,
    "closed_ports": closed_ports
}

# Write it to a JSON file
filename = f"scan_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, "w") as f:
    json.dump(results, f, indent=4)


# Display a summary after the scan is complete
print(f"\nresults saved to {filename}")
print(f"scanned {len(total_ports)} ports")
print(f"open: {[p['port'] for p in open_ports]}")
print(f"closed: {len(closed_ports)} ports")