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


def regex_pass(pattern: str):
    """
    Generates all possible passwords from 'pattern'.
    Each underscore '_' can become any digit [0-9] or be removed entirely.
    """
    expansions = ['']

    for ch in pattern:
        new_expansions = []
        if ch != '_':
            # Just append this character to all existing expansions
            for e in expansions:
                new_expansions.append(e + ch)
        else:
            # we either insert digits '0'..'9', or skip adding anything 
            for e in expansions:
                for digit in '0123456789':
                    new_expansions.append(e + digit)
                new_expansions.append(e)
        expansions = new_expansions

    return expansions


def guess_password(pattern: str):
    first32 = sys.stdin.buffer.read(32)
    if len(first32) < 32:
        print("no password candidates found")
        return
    iv = first32[:16]
    salt = first32[16:32]

    ciphertext = sys.stdin.buffer.read(4096)

    found_any = False

    # For each candidate password, attempt decryption and check if decrypted bytes are ASCII.
    tried = set()  # to avoid duplicates if needed
    for candidate in regex_pass(pattern):
        if candidate in tried:
            continue
        tried.add(candidate)

        # Key derivation
        key = key_stretch(candidate, salt, 16)

        # Create a decryptor
        decryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).decryptor()
        plainblock = decryptor.update(ciphertext) + decryptor.finalize()

        # Check if it's all ASCII
        if plainblock.isascii():
            print(f"found password that seems to work: '{candidate}'")
            found_any = True

    if not found_any:
        print("no password candidates found")


def main():
    args = parse_args()
    guess_password(args.passwordpattern)


if __name__ == "__main__":
    main()
