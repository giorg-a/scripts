import socket
import re


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

    # Check that every octet is within the valid range: 0–255
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
    #
    # Valid TCP/UDP port numbers range from 1 to 65535.
    # The starting port must also be less than or equal to the ending port.
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("invalid port range")
        continue

    # Exit the loop after receiving a valid port range
    break


# Scan every port from start_port through end_port
#
# end_port + 1 is used because Python's range() stops before its
# second value.
for port in range(start_port, end_port + 1):

    # Create a TCP socket.
    # The "with" statement automatically closes the socket afterward.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # Prevent the program from waiting forever on a port
        sock.settimeout(0.4)

        # Try to connect to the target IP and port.
        #
        # connect_ex() returns:
        #   0     if the connection succeeds
        #   other if the connection fails or times out
        result = sock.connect_ex((target, port))

        # Record that this port was scanned
        total_ports.append(port)

        # A result of 0 means the port accepted the TCP connection
        if result == 0:
            open_ports.append(port)
            print(f"port {port}: open")

        # Any other result means the connection was unsuccessful
        else:
            closed_ports.append(port)
            print(f"port {port}: closed")


# Display a summary after the scan is complete
print(f"scanned {len(total_ports)} ports")
print(f"open: {open_ports}")
print(f"closed: {len(closed_ports)} ports")

