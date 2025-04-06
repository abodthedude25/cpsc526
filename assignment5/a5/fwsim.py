# ==============================================================================
# Copyright (C) 2025 Pavol Federl pfederl@ucalgary.ca
# Do not distribute this file.
# ==============================================================================
# This is the only file you need to modify and submit for grading.


# You can use the incomplete code below as a starting point for the assignment.
# The only function you need to implement is fwsim() and it needs to keep
# the same signature. You can delete all the other code.
#
# The incomplete solution does not work for most packets/rules. It is also
# inefficient. And it does not handle blank lines, nor comments. I
# included it it mostly to illustrate how to return results and errors from
# the fwsim() function.


def find_match(rule_lines: list[str], packet: str, rule_fname: str) -> int:
    """helper function - feel free to delete it,
    it does not work very well anyways"""
    pfields = packet.split()
    for line_no, rule in enumerate(rule_lines, 1):
        rfields = rule.split()
        if len(rfields) not in [4, 5]:
            raise Warning(f"{rule_fname}:{line_no}: rule must have 4 or 5 fields")
        iprange = rfields[2].split("/")[0]
        if pfields[0] == rfields[0] and (pfields[1] == iprange or iprange == "*"):
            return line_no
    return 0


def fwsim(rules_fname: str, packets_fname: str) -> list[list[str]]:
    """
    This is the function you need to implement.

    Returns a list of tuples, where each tuple represents the result of 
    matching the packet to a rule. For each packet, it inserts a tuple
        (action, rule_line, direction, ip, port, flag)
    into the result. These are described in the assignment specifications.
    """

    try:
        with open(rules_fname, "r", encoding="ascii") as fp:
            rules = fp.readlines()
        with open(packets_fname, "r", encoding="ascii") as fp:
            packets = fp.readlines()
    except Exception as e:
        # not a good warning - should only include a single filename,
        # a line number, and the error message
        raise Warning(
            f"failed to read rules from '{rules_fname}', "
            f"or packets from '{packets_fname}'"
        ) from e

    # super inefficient implementation below
    # it requires re-parsing of rules for every packet!!!
    results = []
    for pline, packet in enumerate(packets, 1):
        pfields = tuple(packet.split())
        if len(pfields) != 4:
            # this is a much better warning:
            raise Warning(f"{packets_fname}:{pline}: packet needs 4 fields")
        rline = find_match(rules, packet, rules_fname)
        if rline == 0:
            results.append(("default", "") + pfields)
        else:
            results.append((rules[rline - 1].split()[1], str(rline)) + pfields)
    return results
