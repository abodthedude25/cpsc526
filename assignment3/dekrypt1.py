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
    # your code goes here
    pass


def main():
    args = parse_args()
    decrypt_stdin(args.password)


if __name__ == "__main__":
    main()
