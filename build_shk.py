#!/usr/bin/env python

"""
Author: Nick Russo (nickrus@cisco.com)
Purpose: Build a new Surge Hospital Kit (SHK) configuration set.
"""

import random
import string
import ipaddress
import glob
import os
from zipfile import ZipFile
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

    # Build output zip file
    create_zip("outputs")


def create_zip(path_to_zip):
    """
    Create ZIP archive of entire outputs/ directory for easy transporation.
    """
    with ZipFile("shk_configs.zip", "w") as handle:
        for filename in glob.glob(f"{path_to_zip}/**", recursive=True):
            handle.write(filename)


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
            "data_svi10": subnets["data"][-6],
            "biomed_svi20": subnets["biomed"][-6],
            "voice_svi30": subnets["voice"][-6],
            "mgmt_svi40": subnets["mgmt"][-6],
            "mgmt_svi40_hex": hex(int(subnets["mgmt"][-6]))[2:].upper(),
            "special_svi50": subnets["special"][-6],
        },
        "asw1": {"mgmt_svi40": subnets["mgmt"][3]},
        "asw2": {"mgmt_svi40": subnets["mgmt"][4]},
        "asw3": {"mgmt_svi40": subnets["mgmt"][5]},
        "asw4": {"mgmt_svi40": subnets["mgmt"][6]},
        "asw5": {"mgmt_svi40": subnets["mgmt"][7]},
    }

    # Assemble WLANs with SSID names and random plain-text PSKs
    ssid_prefix = f"SHK-WLC-{node['telephony_prefix']}"
    wlan = {
        "data": {"ssid": f"{ssid_prefix}-DATA", "psk": generate_psk()},
        "biomed": {"ssid": f"{ssid_prefix}-BIOMED", "psk": generate_psk()},
        "voice": {"ssid": f"{ssid_prefix}-VOICE", "psk": generate_psk()},
    }

    # Update data dict with new data, then return it
    data.update(
        {
            "telephony_prefix": node["telephony_prefix"],
            "dmvpn_target": node["dmvpn_target"],
            "domain_name": node["domain_name"],
            "subnets": subnets,
            "addr": addr,
            "wlan": wlan,
        }
    )
    return data


def generate_psk(psk_length=8):
    """
    Generate a random alphanumeric string of fixed length.
    Assumes 8 characters by default.
    """
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for i in range(psk_length))


if __name__ == "__main__":
    main()
