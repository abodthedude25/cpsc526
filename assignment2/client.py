#!/bin/env python3
# ==============================================================================
# Copyright (C) 2024 Pavol Federl pfederl@ucalgary.ca
# do not distribute
# ==============================================================================
import argparse
import socket
import sys
import base64
from common import *
try:
    # use readline if possible to improve input()
    import readline
except:
    pass

def parse_args():
    parser = argparse.ArgumentParser(
        prog='client',
        description='client connects to server')
    parser.add_argument('hostname', help='hostname of the server')
    parser.add_argument('port', type=int, help='port where server listens')
    parser.add_argument('-d', '--debug', action='store_true',
                        help="enable debugging output")
    return parser.parse_args()

def handshake(lsock: LineSocket, secret: str):
    challenge = lsock.recv()
    # Compute SHA256 response
    response = compute_sha256(challenge + secret)
    lsock.send(response)
    ack = lsock.recv()
    if ack != "OK":
        print("Failed to connect:" + ack)
        sys.exit(-1)
    print("Connected...")

def handle_command(lsock: LineSocket, cmd: str):
    parts = cmd.split(maxsplit=1)
    command = parts[0] if parts else ""

    try:
        if command == "ls":
            lsock.send(cmd)
            while True:
                line = lsock.recv()
                if line == "---":
                    break
                print(line)
        
        elif command in ["pwd", "cd"]:
            lsock.send(cmd)
            print(lsock.recv())
        
        elif command == "cat":
            lsock.send(cmd)
            content = ""
            while True:
                line = lsock.recv()
                if line == "#":
                    break
                content += line
            try:
                # Decode the base64 content
                binary_content = base64.b64decode(content)
                # For binary files, output directly to stdout buffer
                sys.stdout.buffer.write(binary_content)
            except Exception as e:
                print(content)
                
        elif command == "sha256":
            lsock.send(cmd)
            print(lsock.recv())
        
        elif command == "download":
            parts = cmd.split(maxsplit=1)
            if len(parts) != 2:
                print("Usage: download <filename>")
                return

            filename = parts[1].replace("\ "," ")
            lsock.send(cmd)  # Send original command as is

            # First receive the hash
            response = lsock.recv()
            if response.startswith("ERROR:"):
                print(response)
                return

            remote_hash = response

            # Check local file if it exists
            try:
                with open(filename, 'rb') as f:
                    content = f.read()
                    if content:  # Only compute hash if file is not empty
                        local_hash = compute_sha256(content)
                        if local_hash == remote_hash:
                            print("download skipped - local file matches remote file")
                            # Tell server to skip sending content
                            lsock.send("SKIP")
                            return
            except FileNotFoundError:
                pass  # File doesn't exist, continue with download
            except Exception as e:
                print(f"Error reading local file: {str(e)}")
                return

            # Tell server to proceed with sending content
            lsock.send("CONTINUE")

            # Receive file content
            content = ""
            while True:
                line = lsock.recv()
                if line == "#":
                    break
                content += line

            # Save the file
            try:
                binary_content = base64.b64decode(content)
                with open(filename.split("/")[-1], 'wb') as f:
                    f.write(binary_content)
                print(f"downloaded {len(binary_content)} bytes")
            except Exception as e:
                print(f"Error saving file: {str(e)}")

        elif command == "upload":
            parts = cmd.split(maxsplit=1)
            if len(parts) != 2:
                print("Usage: upload <filename>")
                return
            filename = parts[1].replace("\ ", " ")
            # Compute local file hash
            try:
                with open(filename, 'rb') as f:
                    content = f.read()
                    local_hash = compute_sha256(content)
            except FileNotFoundError:
                print("no such local file")
                return
            except Exception as e:
                print(f"Error: {str(e)}")
                return

            # Start upload process
            lsock.send(cmd)
            lsock.send(local_hash)

            response = lsock.recv()
            if response == "SKIP":
                print("upload skipped - local file matches remote file")
                return
            elif response != "READY":
                print(f"Error: {response}")
                return

            # Send file content
            try:
                encoded = base64.b64encode(content).decode('ascii')
                lsock.send(encoded)
                lsock.send("#")
                
                result = lsock.recv()
                if result == "OK":
                    print(f"uploaded {len(content)} bytes")
                else:
                    print(f"Error: {result}")
            except Exception as e:
                print(f"Error uploading file: {str(e)}")
        
        else:
            lsock.send(cmd)
            reply = lsock.recv()
            print(reply)

    except ConnectionError:
        print("Connection failed. Is the server dead?")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    args = parse_args()
    dbg.enabled = args.debug
    secret = get_secret()
    print(f"connecting to {args.hostname}:{args.port} with {secret=}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.hostname, args.port))
    lsock = LineSocket(sock)
    try:
        handshake(lsock, secret)
        while True:
            try:
                cmd = input("> ").strip()
                handle_command(lsock, cmd)
            except KeyboardInterrupt:
                print("\nDisconnecting...")
                break
    except ConnectionError:
        print("Connection failed. Is the server dead?")
    finally:
        sock.close()

if __name__ == "__main__":
    main()