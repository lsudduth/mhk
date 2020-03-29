#!/usr/bin/env python

"""
Author: Nick Russo (nickrus@cisco.com)
Purpose: Build a new Surge Hospital Kit (SHK) configuration set.
"""

import ipaddress
import glob
import os
from yaml import safe_load
from jinja2 import Environment, FileSystemLoader


def main():
    """
    Execution begins here.
    """

    # Read the input data from file
    with open("inputs.yml", "r") as handle:
        initial = safe_load(handle)

    # Create outputs/ directory if it doesn't exist
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    # Only generate one hub config for the entire SHK run
    j2_env = Environment(loader=FileSystemLoader("."), autoescape=True)
    template = j2_env.get_template("templates/hub.j2")
    config = template.render(data=initial["hub"])

    # Write hub config to output directory (top level)
    with open(f"outputs/hub.txt", "w") as handle:
        handle.write(config)

    # Collect all SHK template files once (not in loop)
    template_files = glob.glob("templates/shk/*.j2")

    # Iterate over each node in the node_list with a counter
    for i, node in enumerate(initial["shk"]):
        # Extract data for each node and update index with offset
        data = process_node(node)
        data["index"] = i + node["index_offset"]
        data["hub"] = initial["hub"]

        # Create per-node output subdirectory
        output_dir = f"outputs/{node['telephony_prefix']}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate all templates
        for template_file in template_files:

            # Load templates and render them
            template = j2_env.get_template(template_file)
            config = template.render(data=data)

            # Write new configs to files with same basename as template
            output_file = os.path.basename(template_file).split(".")[0]
            with open(f"{output_dir}/{output_file}.txt", "w") as handle:
                handle.write(config)


def process_node(node):
    """
    Build a data dictionary from data in each node definition.
    """

    # Initialize empty data dict and collect the two main
    # /23 subnets that make up the greater /22
    data = {}
    network = ipaddress.ip_network(node["ipv4_network"])
    first, second = list(network.subnets())

    # Perform subnetting to collect each individual subnet
    subnets = {
        "full": network,
        "data": first,
        "biomed": list(second.subnets(prefixlen_diff=3))[0],
        "voice": list(second.subnets(prefixlen_diff=3))[1],
        "mgmt": list(second.subnets(prefixlen_diff=4))[4],
        "special": list(second.subnets(prefixlen_diff=5))[10],
        "loopback": list(second.subnets(prefixlen_diff=5))[11],
    }

    # Compute individual IP addresses
    addr = {
        "rtr": {"lb0": subnets["loopback"][1]},
        "dsw": {
            "lb0": subnets["loopback"][2],
            "data_svi10": subnets["data"][-2],
            "biomed_svi20": subnets["biomed"][-2],
            "voice_svi30": subnets["voice"][-2],
            "mgmt_svi40": subnets["mgmt"][-2],
            "special_svi50": subnets["special"][-2],
        },
        "wlc": {
            "mgmt": subnets["mgmt"][1],
            "mgmt_hex": hex(int(subnets["mgmt"][1]))[2:].upper(),
        },
        "asw1": {"mgmt_svi40": subnets["mgmt"][5]},
        "asw2": {"mgmt_svi40": subnets["mgmt"][6]},
        "asw3": {"mgmt_svi40": subnets["mgmt"][7]},
        "asw4": {"mgmt_svi40": subnets["mgmt"][8]},
        "asw5": {"mgmt_svi40": subnets["mgmt"][9]},
    }

    # Update data dict with new data, then return it
    data.update(
        {
            "subnets": subnets,
            "telephony_prefix": node["telephony_prefix"],
            "addr": addr,
        }
    )
    return data


if __name__ == "__main__":
    main()
