# ==============================================================================
# Copyright (C) 2024 Pavol Federl pfederl@ucalgary.ca
# do not distribute
# ==============================================================================
import os
import pathlib
import sys
import hashlib  # Add this import for SHA256

# hardcode your secret here:
_SECRET = None

__all__ = [
    "dbg",
    "LineSocket",
    "get_secret",
    "compute_sha256" 
]

# Add new function for SHA256 computation
def compute_sha256(data):
    sha256_hash = hashlib.sha256()
    if isinstance(data, str):
        data = data.encode('utf-8')
    sha256_hash.update(data)
    return sha256_hash.hexdigest()

def dbg(*args, **kwargs):
    if not dbg.enabled:
        return
    print(dbg.prefix, *args, **kwargs)

dbg.prefix = "dbg:"
dbg.enabled = True

def get_secret():
    # check if hardcoded secret is set
    if _SECRET:
        return _SECRET
    # check environment variable SECRET526
    try:
        return os.environ["SECRET526"]
    except Exception:
        pass
    # check the source directory for .secret526 file
    secret_fname = pathlib.Path(__file__).parent / ".secret526"
    try:
        with secret_fname.open() as fp:
            return fp.readline().strip()
    except Exception:
        pass
    print("No configured secret found.")
    print("Either hardcode one in common.py,")
    print("or use environment variable SECRET526,")
    print("or save one in", secret_fname)
    sys.exit(-1)

class LineSocket:
    """Simple line based protocol.
    Only two methods: send() and recv()
    send() returns one line from socket
    recv() sends string as a line to socket
    """
    MAX_LINE_LENGTH = 2**30
    MAX_READ_BUFF_SIZE = 4096

    def __init__(self, sock, *, max_line_size=120) -> None:
        self._sock = sock
        self._rbuff = ""

    def send(self, string) -> None:
        string += "\n"
        self._sock.sendall(string.encode("ascii", "ignore"))

    def recv(self) -> str:
        while True:
            # check if we have a full line in buffer
            first_line, sep, rest = self._rbuff.partition('\n')
            if sep:
                # full line found, remove it from buffer
                self._rbuff = rest
                if len(first_line) > self.MAX_LINE_LENGTH:
                    dbg(f"received line is too long "
                        f"(>{self.MAX_LINE_LENGTH} chars)")
                    raise ConnectionError("line too long")
                return first_line
            if len(self._rbuff) > self.MAX_LINE_LENGTH:
                dbg(f"incoming line is too long (>{self.MAX_LINE_LENGTH} chars)")
                raise ConnectionError("line too long")
            # read more data into buffer
            part = self._sock.recv(self.MAX_READ_BUFF_SIZE)
            if len(part) == 0:
                self._sock.close()
                dbg("unexpected client disconnect")
                raise ConnectionError
            self._rbuff += part.decode('ascii')

    # Add new helper methods for file operations
    def send_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                encoded = content.encode('base64').decode('ascii')
                self.send(encoded)
                self.send("#EOF#")  # End marker
                return True
        except Exception as e:
            self.send(f"ERROR: {str(e)}")
            return False

    def recv_file(self, filepath):
        try:
            content = ""
            while True:
                line = self.recv()
                if line == "#EOF#":
                    break
                content += line
            with open(filepath, 'wb') as f:
                f.write(content.encode('ascii').decode('base64'))
            return True
        except Exception as e:
            return False