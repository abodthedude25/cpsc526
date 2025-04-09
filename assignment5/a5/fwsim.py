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

#Authored By: Issam Akhtar, Abdelrehman Abbas

def ip2int(ip_str) -> int:
    if ip_str == "*":
        return 0

    try:
        oct = ip_str.split('.')
        if len(oct) != 4:
            return None  # not enough octets in ip

        for o in oct:
            value = int(o)
            if value < 0 or value > 255:
                return None  # Invalid

        # convert to int32: a.b.c.d = (a << 24) | (b << 16) | (c << 8) | d
        return (int(oct[0]) << 24) | (int(oct[1]) << 16) | (int(oct[2]) << 8) | int(oct[3])
    except ValueError:
        return None


def cidr_ip_range(ip_int, cidr_range) -> bool:
    if cidr_range == "*":
        return True

    try:
        ip_str, prefix_len_str = cidr_range.split('/')
        prefix_len = int(prefix_len_str)

        if prefix_len < 0 or prefix_len > 32:
            return None

        base_ip_int = ip2int(ip_str)

        if base_ip_int is None:
            return None

        # mask based on prefix length and check if in range
        return (ip_int & 0xFFFFFFFF << (32 - prefix_len)) == (base_ip_int & 0xFFFFFFFF << (32 - prefix_len))

    except ValueError:
        return None


def get_ports(ports_str):
    if ports_str == "*":
        return ["*"]

    try:
        ports = []
        for port_str in ports_str.split(','):
            if port_str:  # skip empty
                port = int(port_str)
                if port < 0 or port > 65535:
                    return None
                ports.append(port)
        return ports
    except ValueError:
        return None


def rule_packet_comp(rule, packet, flag_value=None):
    r_dir, r_action, r_range, r_ports, *r_flags = rule
    p_dir, p_ip, p_port, p_flag = packet

    if r_dir != p_dir:
        return False

    packet_ip = ip2int(p_ip)
    result = cidr_ip_range(packet_ip, r_range)

    if result is None:
        return None

    if not result:
        return False

    rule_ports_parsed = get_ports(r_ports)

    if rule_ports_parsed is None:
        return None

    if ("*" not in rule_ports_parsed and int(p_port) not in rule_ports_parsed):
        return False

    if r_flags and r_flags[0] == "established" and p_flag != "1":
        return False

    return True


def get_rules(line, i, filename):
    fields = line.split()

    if len(fields) not in [4, 5]:
        raise Warning(f"{filename}:{i}: rule must have 4 or 5 fields")

    if fields[0] not in ["in", "out"]:
        raise Warning(
            f"{filename}:{i}: invalid direction '{fields[0]}', must be 'in' or 'out'")

    if fields[1] not in ["accept", "drop", "deny"]:
        raise Warning(
            f"{filename}:{i}: invalid action '{fields[1]}', must be 'accept','drop', or 'deny'")

    if fields[2] != "*":
        if "/" not in fields[2]:
            raise Warning(
                f"{filename}:{i}: invalid IP range '{fields[2]}', missing CIDR prefix")

        ip_str, prefix = fields[2].split("/", 1)

        if "/" in prefix:
            raise Warning(
                f"{filename}:{i}: invalid CIDR notation '{fields[2]}'")

        ip_int = ip2int(ip_str)
        if ip_int is None:
            raise Warning(f"{filename}:{i}: invalid IP address '{ip_str}'")

        try:
            prefix = int(prefix)
            if prefix < 0 or prefix > 32:
                raise Warning(
                    f"{filename}:{i}: invalid CIDR prefix '{prefix}', must be between 0 and 32")
        except ValueError:
            raise Warning(
                f"{filename}:{i}: invalid CIDR prefix '{prefix}', must be an integer")

    ports = get_ports(fields[3])

    if ports is None:
        raise Warning(f"{filename}:{i}: invalid ports '{fields[3]}'")

    if len(fields) == 5 and fields[4] != "established":
        raise Warning(
            f"{filename}:{i}: invalid flag '{fields[4]}', only 'established' is allowed")

    return fields


def get_packet(line, i, filename):
    fields = line.split()

    if len(fields) != 4:
        raise Warning(f"{filename}:{i}: packet needs 4 fields")

    if fields[0] not in ["in", "out"]:
        raise Warning(
            f"{filename}:{i}: invalid direction '{fields[0]}', must be 'in' or 'out'")

    ip_int = ip2int(fields[1])

    if ip_int is None:
        raise Warning(f"{filename}:{i}: invalid IP address '{fields[1]}'")

    try:
        port = int(fields[2])
        if port < 0 or port > 65535:
            raise Warning(
                f"{filename}:{i}: invalid port '{fields[2]}', must be between 0 and 65535")

    except ValueError:
        raise Warning(
            f"{filename}:{i}: invalid port '{fields[2]}', must be an integer")

    if fields[3] not in ["0", "1"]:
        raise Warning(
            f"{filename}:{i}: invalid flag '{fields[3]}', must be '0' or '1'")

    return fields


def fwsim(rules_fname: str, packets_fname: str) -> list[list[str]]:
    """
    This function implements the firewall simulator.

    Returns a list of tuples, where each tuple represents the result of 
    matching the packet to a rule. For each packet, it inserts a tuple
        (action, rule_line, direction, ip, port, flag)
    into the result. 
    """
    results = []
    rules = []
    line_num = []

    try:
        # read rules
        with open(rules_fname, "r", encoding="ascii") as fp:
            rule_lines = fp.readlines()

        for i, line in enumerate(rule_lines, 1):  # enumerate also keeps iter num
            # comments
            if '#' in line:
                line = line[:line.find('#')]
            l = line.strip()

            if not l:
                continue

            rule = get_rules(l, i, rules_fname)
            rules.append(rule)
            line_num.append(i)

        # read packets
        with open(packets_fname, "r", encoding="ascii") as fp:
            packet_lines = fp.readlines()

        for i, line in enumerate(packet_lines, 1):
            # commenrs
            if '#' in line:
                line = line[:line.find('#')]
            l = line.strip()

            if not l:
                continue

            packet = get_packet(l, i, packets_fname)
            # match flag
            match = False

            for i, rule in enumerate(rules):
                result = rule_packet_comp(rule, packet)

                if result is None:
                    # final check for errors
                    raise Warning(
                        f"{rules_fname}:{line_num[i]}: error processing rule")

                if result:
                    # result(action, rule_line, direction, ip, port, flag)
                    results.append(
                        (rule[1], str(line_num[i]), packet[0], packet[1], packet[2], packet[3]))
                    match = True
                    break

            # no match then use default
            if not match:
                results.append(
                    ("default", "", packet[0], packet[1], packet[2], packet[3]))

    except (IOError, FileNotFoundError) as e:
        raise Warning(f"Error opening file: {str(e)}")
    except KeyboardInterrupt:
        raise Warning(f"Program killed")

    return results