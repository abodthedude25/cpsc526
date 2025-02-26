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


def dekrypt(p1, c1, c2):
    # your code goes here
    # hint: how do you xor binary data?
    pass


def main():
    args = parse_args()
    dekrypt(args.p1, args.c1, args.c2)


if __name__ == "__main__":
    main()
