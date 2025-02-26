#!/bin/env python3
# ==============================================================================
# Copyright (C) 2025 Pavol Federl pfederl@ucalgary.ca
# do not distribute
# ==============================================================================

# you can use this file as a starting point for Task 2

import argparse
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


def parse_args():
    parser = argparse.ArgumentParser(
        prog='dekrypt2',
        description='AES pasword guesser',
    )
    parser.add_argument('passwordpattern', help='password pattern')
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


def guess_password(pattern: str):
    # your code goes here
    pass


def main():
    args = parse_args()
    guess_password(args.passwordpattern)


if __name__ == "__main__":
    main()
