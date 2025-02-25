#!/bin/env python3
# ==============================================================================
# Copyright (C) 2024 Pavol Federl pfederl@ucalgary.ca
# do not distribute
# ==============================================================================
import argparse
import pathlib
import socket
import secrets
import subprocess
import os
import base64
from common import *

def parse_args():
    parser = argparse.ArgumentParser(
        prog='server',
        description='server that the client connects to')
    parser.add_argument('port', type=int, help='port where server listens')
    parser.add_argument('-d', '--debug', action='store_true',
                        help="enable debugging output")
    return parser.parse_args()

def make_listening_socket(hostname, port):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ss.bind((hostname, port))
    ss.listen(1)
    return ss

def handshake(lsock: LineSocket, secret: str):
    dbg("executing handshake")
    challenge = secrets.token_hex(8)  # At least 8 characters
    lsock.send(challenge)
    
    # Compute expected SHA256 response
    expected_response = compute_sha256(challenge + secret)
    dbg("expecting response", expected_response)
    
    line = lsock.recv()
    if line != expected_response:
        lsock.send("incorrect challenge response")
        lsock._sock.close()
        dbg("handshake failure")
        raise ConnectionAbortedError
    
    lsock.send("OK")
    dbg("handshake success")

def handle_cd(lsock, args):
    try:
        os.chdir(args[1])
        lsock.send(str(pathlib.Path.cwd()))
    except Exception as e:
        lsock.send(f"cd: {str(e)}")

def handle_cat(lsock, args):
    filename = ' '.join(arg.strip() for arg in args[1:]).replace("\\", "")
    try:
        with open(filename, 'rb') as f:
            content = f.read()
            lsock.send(base64.b64encode(content).decode('ascii'))
            lsock.send("#")
    except Exception as e:
        print(e)
        lsock.send(f"cat: {str(e)}")
        lsock.send("#")


def handle_sha256(lsock, args):
    filename = ' '.join(arg.strip() for arg in args[1:]).replace("\\", "")
    try:
        with open(filename, 'rb') as f:
            content = f.read()
            digest = compute_sha256(content)
            lsock.send(digest)
    except Exception as e:
        lsock.send(f"sha256: {str(e)}")
def handle_download(lsock, args):
    if len(args) < 2:
        lsock.send("ERROR: Usage: download <filename>")
        return
    filename = ' '.join(arg.strip() for arg in args[1:]).replace("\\", "")
    try:
        # First send hash
        with open(filename, 'rb') as f:
            content = f.read()
            digest = compute_sha256(content)
            lsock.send(digest)

        # Wait for client decision
        decision = lsock.recv()
        if decision == "SKIP":
            return  # Client has matching file, no need to send content

        # Send the actual content
        lsock.send(base64.b64encode(content).decode('ascii'))
        lsock.send("#")
    except Exception as e:
        lsock.send(f"ERROR: {str(e)}")
        
def handle_upload(lsock, args):
    try:
        # Get client's file hash
        client_hash = lsock.recv()
        
        # Check if file exists and compare hashes
        filename = ' '.join(arg.strip() for arg in args[1:]).replace("\\", "")
        print(f'writing: {filename}')
        try:
            with open(filename, 'rb') as f:
                content = f.read()
                server_hash = compute_sha256(content)
                if server_hash == client_hash:
                    lsock.send("SKIP")
                    return
        except FileNotFoundError:
            pass

        # Ready to receive file
        lsock.send("READY")
        
        # Receive file content
        content = ""
        while True:
            line = lsock.recv()
            if line == "#":
                break
            content += line
        
        # Save file
        binary_content = base64.b64decode(content)
        with open(args[1], 'wb') as f:
            f.write(binary_content)
        lsock.send("OK")
    except Exception as e:
        lsock.send(f"ERROR: {str(e)}")

def execute_command(lsock: LineSocket, cmd):
    dbg(f"executing command {repr(cmd)}")
    args = cmd.split()
    if not args:
        lsock.send("empty line? really?")
        return

    try:
        if args[0] == "ls":
            output = subprocess.run(["ls"]+args[1:], capture_output=True)
            stdout = output.stdout.decode("ascii", "ignore").split("\n")
            stderr = output.stderr.decode("ascii", "ignore").split("\n")
            all = stdout + stderr + ["---"]
            all = [line for line in all if len(line)]
            for line in all:
                lsock.send(line)
        elif args[0] == "pwd":
            lsock.send(str(pathlib.Path.cwd()))
        elif args[0] == "cd":
            handle_cd(lsock, args)
        elif args[0] == "cat":
            handle_cat(lsock, args)
        elif args[0] == "sha256":
            handle_sha256(lsock, args)
        elif args[0] == "download":
            handle_download(lsock, args)
        elif args[0] == "upload":
            handle_upload(lsock, args)
        else:
            lsock.send(f"unknown command {cmd}")
    except Exception as e:
        lsock.send(f"Error: {str(e)}")

def serve_client(sock, secret):
    try:
        lsock = LineSocket(sock)
        handshake(lsock, secret)
        while True:
            cmd = lsock.recv()
            execute_command(lsock, cmd)
    except ConnectionError:
        pass
    sock.close()
    dbg("client disconnected")

def main():
    args = parse_args()
    dbg.enabled = args.debug
    secret = get_secret()
    dbg(f"using {secret=}")
    my_hostname = socket.gethostname()
    dbg(f"starting server on port {args.port}")
    with make_listening_socket(my_hostname, args.port) as ss:
        while True:
            dbg(f"")
            dbg(f"=== listening ==========================================================")
            dbg(f"connect with:")
            dbg(f"  SECRET526={secret} ./client.py {my_hostname} {args.port}")
            dbg(f"  nc {my_hostname} {args.port}")
            (client_socket, client_addr) = ss.accept()
            dbg(f"client connected from {client_addr}")
            serve_client(client_socket, secret)

if __name__ == "__main__":
    main()