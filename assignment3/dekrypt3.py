#!/bin/env python3
# ==============================================================================
# Copyright (C) 2025 Pavol Federl pfederl@ucalgary.ca
# do not distribute
# ==============================================================================

# you can use this file as a starting point for Task 3

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        prog='dekrypt3',
        description='''
        assuming c1=enc_aes_ctr(p1) and c2=enc_aes_ctr(p2) using the same password,
        this program tries to figure out p2, without knowing the password.
        This is possible if the nonces used to produce c1 and c2 were the same.
        '''
    )
    parser.add_argument('p1', help='plaintext1')
    parser.add_argument('c1', help='ciphertext1')
    parser.add_argument('c2', help='ciphertext2')
    return parser.parse_args()

def dekrypt(p1file, c1file, c2file):
    # Read P1 
    with open(p1file, 'rb') as f:
        p1 = f.read()

    # Read C1 
    with open(c1file, 'rb') as f:
        c1 = f.read()
    # Read C2 
    with open(c2file, 'rb') as f:
        c2 = f.read()

    # Each ciphertext must have at least 32 bytes (IV+salt)
    if len(c1) < 32 or len(c2) < 32:
        print("Error: cannot decrypt")
        return

    # Check if IV+salt match
    if c1[:32] != c2[:32]:
        print("Error: cannot decrypt")
        return

    # c1_enc is the portion after the 32-byte header
    c1_enc = c1[32:]
    c2_enc = c2[32:]

    # We can only recover as many bytes as we have in c1_enc, c2_enc, and p1
    n = min(len(p1), len(c1_enc), len(c2_enc))
    if n == 0:
        print("Error: cannot decrypt")
        return

    # Recover p2 for these n bytes
    p2_recovered = bytearray(n)
    for i in range(n):
        # p2[i] = c2_enc[i] XOR c1_enc[i] XOR p1[i]
        p2_recovered[i] = c2_enc[i] ^ c1_enc[i] ^ p1[i]

    # Output the recovered portion this might be text or binary.
    try:
        print(p2_recovered.decode('utf-8', errors='replace'), end='')
    except:
        # fallback to raw bytes
        sys.stdout.buffer.write(p2_recovered)

def main():
    args = parse_args()
    dekrypt(args.p1, args.c1, args.c2)


if __name__ == "__main__":
    main()
