#!/bin/env python3
# ==============================================================================
# Copyright (C) 2025 Pavol Federl pfederl@ucalgary.ca
# Do not distribute this file.
# ==============================================================================
# Do not modify this file. Your fwsim.py must work with an umodified fw.py file.
# Do not submit this file for grading. We will grade your code with our own
# version of fw.py.

import argparse
import fwsim


def format_result(result: list[list[str]]) -> str:
    '''format one tuple as a string'''
    action, rule_line, direction, ip, port, flag = [str(r) for r in result]
    prefix = f"{action}({rule_line})"
    suffix = f"{direction:3} {ip:15} {port:5} {flag}"
    return f"{prefix:12} {suffix}"


def parse_args():
    '''parse command lines'''
    parser = argparse.ArgumentParser(
        prog='fw',
        description='firewall simulator',
    )
    parser.add_argument('rulesfname', help='filename with firewall rules')
    parser.add_argument('packetsfname', help='filename with packets')
    return parser.parse_args()


def main():
    '''entry point to driver'''
    args = parse_args()
    try:
        results = fwsim.fwsim(args.rulesfname, args.packetsfname)
    except Warning as e:
        print(f"Simulator error: {e}")
        return
    for result in results:
        assert type(result) in [list, tuple]
        assert len(result) == 6
        print(format_result(result))


if __name__ == "__main__":
    main()
