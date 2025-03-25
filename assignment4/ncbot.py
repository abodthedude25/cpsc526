#!/usr/bin/env python3

import sys
import socket
import time
import hashlib

def compute_mac(nonce, secret):
    """Compute the first 8 hex digits of SHA-256(nonce + secret)."""
    combo = nonce + secret
    sha_val = hashlib.sha256(combo.encode('utf-8')).hexdigest()
    return sha_val[:8]

def connect_loop(host, port, nick, secret):
    """
    Continuously attempt to connect to the server.
    Once connected, send the join message and then handle commands.
    If disconnected unexpectedly, keep retrying after 5s sleep.
    """
    seen_nonces = set()
    command_count = 0

    while True:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, port))
            # Once connected, reset to no timeout for reading lines
            s.settimeout(None)

            print("Connected.")
            # Send the joined message
            join_msg = f"-joined {nick}\n"
            s.sendall(join_msg.encode('utf-8'))

            # Handle commands
            command_count, should_exit = handle_commands(
                s, nick, secret, seen_nonces, command_count
            )

            if should_exit:
                # If we exit normally via 'shutdown', just return
                return

            # If we somehow drop out of handle_commands without a normal shutdown,
            # we must have been disconnected or encountered an error. 
            # We'll close the socket and loop to reconnect.
            print("Disconnected.")

        except Exception as e:
            print("Failed to connect.")
            if s:
                s.close()
            time.sleep(5)  # Wait before retrying

def handle_commands(sock, nick, secret, seen_nonces, command_count):
    """
    Read commands from the server, parse and authenticate them.
    Execute if valid. Return the updated command_count and whether
    we should exit the entire bot (True for exit, False otherwise).
    """
    # We’ll read lines in a loop until an exception occurs (disconnect or read error).
    while True:
        line = sock.readline() if hasattr(sock, 'readline') else sock.recv(4096)
        if not line:
            # Connection closed or broken
            return command_count, False

        # If we used sock.recv, data might come in partial; try to split by lines
        if isinstance(line, bytes):
            lines = line.decode('utf-8', errors='ignore').split('\n')
        else:
            lines = line.split('\n')

        for cmdline in lines:
            cmdline = cmdline.strip()
            if not cmdline:
                continue
            parts = cmdline.split()
            if len(parts) < 3:
                # Not a valid command format, ignore
                continue

            nonce, mac, command = parts[0], parts[1], parts[2]
            args = parts[3:]

            # AUTHENTICATE
            if nonce in seen_nonces:
                # Already used nonce, ignore
                continue

            computed = compute_mac(nonce, secret)
            if computed != mac:
                # Invalid MAC
                continue

            # Mark nonce as used
            seen_nonces.add(nonce)
            # We have a valid command
            command_count += 1

            if command == "status":
                msg = f"-status {nick} {command_count}\n"
                sock.sendall(msg.encode('utf-8'))

            elif command == "shutdown":
                msg = f"-shutdown {nick}\n"
                sock.sendall(msg.encode('utf-8'))
                sock.close()
                return command_count, True  # indicates normal exit

            elif command == "attack":
                # Usage: attack <hostname>:<port>
                if len(args) < 1:
                    # Missing argument, ignore
                    continue
                target = args[0]
                attack_status = do_attack(target, nick, nonce)
                sock.sendall(attack_status.encode('utf-8'))

            elif command == "move":
                # Usage: move <hostname>:<port>
                if len(args) < 1:
                    # Missing argument
                    continue
                move_target = args[0]
                move_msg = f"-move {nick}\n"
                sock.sendall(move_msg.encode('utf-8'))
                sock.close()
                # Disconnect from current server, connect to new one
                # parse the new <hostname>:<port>
                hostport = move_target.strip().split(":")
                if len(hostport) == 2:
                    new_host, new_port = hostport[0], int(hostport[1])
                    # Reconnect loop to the new server
                    # We keep the same seen_nonces and command_count
                    reconnect_to_new(
                        new_host, new_port, nick, secret, seen_nonces, command_count
                    )
                # After returning from reconnect_to_new, we basically
                # are done with the old server. We'll attempt to reconnect
                # if needed. So just return here to stop reading old socket.
                return command_count, False

            else:
                # Unknown command, ignore
                continue

def do_attack(target, nick, nonce):
    """
    Attempt to connect to <hostname>:<port> and send a line:
       <nick> <nonce>
    Then close the connection.
    Return a message string of the form:
       "-attack <nick> OK\n" or
       "-attack <nick> FAIL <error-reason>\n"
    """
    try:
        host, port_str = target.split(":")
        port = int(port_str)
    except:
        return f"-attack {nick} FAIL invalid-target\n"

    # Attempt connection with 3s timeout
    try:
        with socket.create_connection((host, port), timeout=3) as s:
            attack_line = f"{nick} {nonce}\n"
            s.sendall(attack_line.encode('utf-8'))
        # If we reach here, we were successful
        return f"-attack {nick} OK\n"
    except socket.timeout:
        return f"-attack {nick} FAIL timeout\n"
    except Exception as e:
        # Could be ConnectionRefusedError, socket.gaierror, etc.
        reason = str(e).lower().replace(" ", "_")
        return f"-attack {nick} FAIL {reason}\n"

def reconnect_to_new(host, port, nick, secret, seen_nonces, command_count):
    """
    Connects to the new server location and continues reading commands
    until an exception or shutdown. This is a separate connect loop
    specifically for 'move'.
    """
    while True:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, port))
            s.settimeout(None)
            print("Connected.")
            # Send join message
            join_msg = f"-joined {nick}\n"
            s.sendall(join_msg.encode('utf-8'))

            # Reuse handle_commands in a loop
            command_count, should_exit = handle_commands(
                s, nick, secret, seen_nonces, command_count
            )
            if should_exit:
                return
            print("Disconnected.")
        except Exception as e:
            print("Failed to connect.")
            if s:
                s.close()
            time.sleep(5)  # keep retrying

def main():
    if len(sys.argv) != 4:
        print("Usage: ./ncbot.py <hostname>:<port> <nick> <secret>")
        sys.exit(1)

    hostport = sys.argv[1].split(":")
    if len(hostport) != 2:
        print("Error: invalid <hostname>:<port>")
        sys.exit(1)

    host = hostport[0]
    port = int(hostport[1])
    nick = sys.argv[2]
    secret = sys.argv[3]

    connect_loop(host, port, nick, secret)

if __name__ == "__main__":
    main()
