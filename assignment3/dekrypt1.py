#!/bin/env python3
# ==============================================================================
# Copyright (C) 2025 Pavol Federl pfederl@ucalgary.ca
# do not distribute
# ==============================================================================

# you can use this file as a starting point for Task 1

import argparse
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


def parse_args():
    parser = argparse.ArgumentParser(
        prog='dekrypt1',
        description='AES decryptor',
    )
    parser.add_argument('password', help='password used for decryption')
    return parser.parse_args()


def key_stretch(password: str, salt: bytes, key_len: int) -> bytes:
    '''
    converts a text password to a key(bytes) suitable for AES
    '''
    key = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_len,
        salt=salt,
        iterations=10
    ).derive(password.encode())
    return key


def decrypt_stdin(password: str):
    raw = sys.stdin.buffer.read(32)
    if len(raw) < 32:
        # Not enough data to even contain IV+salt
        return  # or raise an error

    iv = raw[:16]
    salt = raw[16:32]

    # Derive the AES-128 key using PBKDF2 same as in enkrypt.py
    key = key_stretch(password, salt, 16)

    # Create decryptor object with AES CTR using the same key & IV
    decryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).decryptor()

    # Decrypt the rest of the input in chunks, writing plaintext to stdout
    while True:
        block = sys.stdin.buffer.read(4096)
        if not block:
            break
        pblock = decryptor.update(block)
        sys.stdout.buffer.write(pblock)

    # Finalize the decryption
    pblock = decryptor.finalize()
    sys.stdout.buffer.write(pblock)

def main():
    args = parse_args()
    decrypt_stdin(args.password)

if __name__ == "__main__":
    main()