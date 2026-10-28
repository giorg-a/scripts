import socket
import re
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import sys
import ipaddress 
import errno

# Lists used to store scan results
total_ports = []
open_ports = []
closed_ports = []
filtered_ports = []


def parse_target(raw):
    """return normalised IPv4 or raise the ValueError"""
    return str(ipaddress.IPv4Address(raw.strip()))

while True:
    try:
        target = parse_target(input("target IP: "))
        break
    except ValueError:
        print("invalid IP!")
    
    except KeyboardInterrupt:
        print("session interrupted")
        sys.exit()



# Ask for the starting and ending ports
while True:
    try:
        start_port = int(input("start port: "))
        end_port = (input("end port(leave blank for a single port): "))
        if end_port == "":
             end_port = start_port  
        else:
            end_port = int(end_port)
        

    # This runs if the user enters something that is not a number
    except ValueError:
        print("enter only numbers!")
        continue
    
    except KeyboardInterrupt:
        print("session interrupted")
        sys.exit()


    # Check that the port range is valid
    # Valid TCP/UDP port numbers range from 1 to 65535.
    # The starting port must also be less than or equal to the ending port.
    
    if not (1 <= start_port <= 65535):
        print("start port must be between 1 and 65535")
        continue
    if not (1 <= end_port <= 65535):
        print("end port must be between 1 and 65535")
        continue
    if end_port < start_port:
        print("end port can't be less than start port")
        continue
    # Exit the loop after receiving a valid port range
    break

def scan_port(target, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        result = sock.connect_ex((target, port))

        if result == 0:
            banner = "no banner"
            try:
                sock.settimeout(1)
                data = sock.recv(1024)
                if data:
                    banner = data.decode(errors="ignore").strip()
            except (socket.timeout, ConnectionResetError, OSError):
                pass
            return {"port": port, "status": "open", "banner": banner}

        elif result == errno.ECONNREFUSED:
            return {"port": port, "status": "closed", "banner": None}

        else:
            return {"port": port, "status": "filtered", "banner": None}

# "Pre-fill" the target argument so each worker only needs to be
# handed a port number. scan_with_target(80) now behaves exactly
# like calling scan_port(target, 80).
scan_with_target = partial(scan_port, target)

# Scan every port from start_port through end_port, but now up to
# max_workers ports are scanned AT THE SAME TIME instead of one by
# one. executor.map() still returns results in port order, even
# though the actual scanning happens out of order behind the scenes.
try:
    with ThreadPoolExecutor(max_workers=100) as executor:
        all_outcomes = executor.map(scan_with_target, range(start_port, end_port + 1))

        for outcome in all_outcomes:
            total_ports.append(outcome["port"])

            if outcome["status"] == "open":
                open_ports.append({"port": outcome["port"], "banner": outcome["banner"]})
                print(f"port {outcome['port']}: open ({outcome['banner']})")

            elif outcome["status"] == "closed":
                closed_ports.append(outcome["port"])

            elif outcome["status"] == "filtered":
                filtered_ports.append(outcome["port"])
                print(f"port {outcome['port']}: filtered")
        
except KeyboardInterrupt:
    print("\nsession interrupted")
    executor.shutdown(wait=False, cancel_futures=True)
    sys.exit()

# Build a dictionary holding everything about this scan
results = {
    "target": target,
    "scan_time": datetime.now().isoformat(),
    "total_scanned": len(total_ports),
    "port_range": {"start": start_port, "end": end_port},
    "open_ports": (open_ports),
    "closed_count": len(closed_ports),
    "filtered_count": len(filtered_ports)
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
print(f"filtered: {len(filtered_ports)} ports")
