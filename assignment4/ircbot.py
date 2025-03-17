#!/usr/bin/env python3

import sys
import socket
import time
import hashlib
import random
import string
from typing import Set, Optional, Tuple, Dict, List, Any

def compute_mac(nonce: str, secret: str) -> str:
    combo = nonce + secret
    sha_val = hashlib.sha256(combo.encode('utf-8')).hexdigest()
    return sha_val[:8]

def generate_random_nick() -> str:
    prefix = "bot_"
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return prefix + suffix

class IRCBot:
    def __init__(self, host: str, port: int, channel: str, secret: str):
        self.host: str = host
        self.port: int = port
        self.channel: str = channel
        self.secret: str = secret
        self.nick: str = generate_random_nick()
        self.seen_nonces: Set[str] = set()
        self.command_count: int = 0
        self.connected: bool = False
        self.socket: Optional[socket.socket] = None
        
    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            self.send(f"NICK {self.nick}")
            self.send(f"USER {self.nick} 0 * :{self.nick}")
            
            data_buffer = ""
            while True:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    return False
                
                data_buffer += data
                lines = data_buffer.split('\n')
                data_buffer = lines.pop() if lines else ""
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith("PING"):
                        pong_resp = line.replace("PING", "PONG", 1)
                        self.send(pong_resp)
                    
                    if " 001 " in line:
                        self.send(f"JOIN #{self.channel}")
                        self.connected = True
                        
                        self.send_message(f"-joined {self.nick}")
                        print(f"Connected to {self.host}:{self.port} and joined #{self.channel}")
                        return True
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            self.connected = False
            return False
    
    def send(self, message: str) -> None:
        if self.socket:
            self.socket.sendall(f"{message}\r\n".encode('utf-8'))
    
    def send_message(self, message: str) -> None:
        self.send(f"PRIVMSG #{self.channel} :{message}")
    
    def run(self) -> None:
        while True:
            if not self.connected:
                print("Attempting to connect...")
                if self.connect():
                    print("Connected.")
                else:
                    print("Failed to connect.")
                    time.sleep(5)
                    continue
            
            try:
                if not self.socket:
                    self.connected = False
                    continue
                    
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    print("Disconnected.")
                    self.connected = False
                    self.socket = None
                    time.sleep(5)
                    continue
                
                lines = data.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith("PING"):
                        pong = line.replace("PING", "PONG", 1)
                        self.send(pong)
                        continue
                    
                    if "ERROR" in line or ("KICK" in line and self.nick in line):
                        print("Disconnected.")
                        self.connected = False
                        if self.socket:
                            self.socket.close()
                            self.socket = None
                        time.sleep(5)
                        break
                    
                    if "PRIVMSG" in line and f"#{self.channel}" in line:
                        message_start = line.find(" :", line.find("PRIVMSG")) + 2
                        if message_start != -1:
                            message = line[message_start:]
                            self.handle_command(message)
            
            except Exception as e:
                print(f"Error while running: {e}")
                self.connected = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
                time.sleep(5)
    
    def handle_command(self, message: str) -> None:
        parts = message.split()
        if len(parts) < 3:
            return
        
        nonce, mac, command = parts[0], parts[1], parts[2]
        args = parts[3:]
        
        if nonce in self.seen_nonces:
            return
        
        computed_mac = compute_mac(nonce, self.secret)
        if computed_mac != mac:
            return
        
        self.seen_nonces.add(nonce)
        self.command_count += 1
        
        if command == "status":
            self._handle_status()
        elif command == "shutdown":
            self._handle_shutdown()
        elif command == "attack" and args:
            self._handle_attack(args[0], nonce)
        elif command == "move" and args:
            self._handle_move(args[0])
    
    def _handle_status(self) -> None:
        self.send_message(f"-status {self.nick} {self.command_count}")
    
    def _handle_shutdown(self) -> None:
        self.send_message(f"-shutdown {self.nick}")
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        sys.exit(0)
    
    def _handle_attack(self, target: str, nonce: str) -> None:
        attack_status = self.do_attack(target, nonce)
        self.send_message(attack_status)
    
    def _handle_move(self, target: str) -> None:
        self.send_message(f"-move {self.nick}")
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        try:
            new_host, new_port_str = target.split(":")
            new_port = int(new_port_str)
            
            new_bot = IRCBot(new_host, new_port, self.channel, self.secret)
            new_bot.seen_nonces = self.seen_nonces.copy()
            new_bot.command_count = self.command_count
            
            new_bot.run()
            sys.exit(1)
        except Exception as e:
            print(f"Failed to move to new server: {e}")
            self.connected = False
            time.sleep(5)
    
    def do_attack(self, target: str, nonce: str) -> str:
        try:
            host, port_str = target.split(":")
            port = int(port_str)
        except ValueError:
            return f"-attack {self.nick} FAIL invalid-target"
        
        try:
            with socket.create_connection((host, port), timeout=3) as s:
                attack_line = f"{self.nick} {nonce}\n"
                s.sendall(attack_line.encode('utf-8'))
            return f"-attack {self.nick} OK"
        except socket.timeout:
            return f"-attack {self.nick} FAIL timeout"
        except Exception as e:
            reason = str(e).lower().replace(" ", "_")
            return f"-attack {self.nick} FAIL {reason}"

def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: ./ircbot.py <hostname>:<port> <channel> <secret>")
        sys.exit(1)
    
    hostport = sys.argv[1].split(":")
    if len(hostport) != 2:
        print("Error: invalid <hostname>:<port> format")
        sys.exit(1)
    
    host = hostport[0]
    try:
        port = int(hostport[1])
    except ValueError:
        print("Error: port must be a number")
        sys.exit(1)
    
    channel = sys.argv[2]
    secret = sys.argv[3]
    
    bot = IRCBot(host, port, channel, secret)
    bot.run()

if __name__ == "__main__":
    main()