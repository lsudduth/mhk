#!/usr/bin/env python

"""
Author: Nick Russo (nickrus@cisco.com)
Purpose: Build a new Mobile Hospital Kit (MHK) configuration set.
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

    with open("inputs.yml", "r") as handle:
        initial = safe_load(handle)
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    for i, node in enumerate(initial["node_list"]):
        data = process_node(node)
        data["index"] = i + node["index_offset"]

        j2_env = Environment(loader=FileSystemLoader("."), autoescape=True)
        template_files = glob.glob("templates/*.j2")
        output_dir = f"outputs/{node['telephony_prefix']}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for template_file in template_files:
            template = j2_env.get_template(template_file)
            config = template.render(data=data)
            output_file = os.path.basename(template_file).split(".")[0]
            with open(f"{output_dir}/{output_file}.txt", "w") as handle:
                handle.write(config)


def process_node(node):
    """
    Build a data dictionary from data in each node definition.
    """

    data = {}
    network = ipaddress.ip_network(node["ipv4_network"])
    first, second = list(network.subnets())
    subnets = {
        "data": first,
        "biomed": list(second.subnets(prefixlen_diff=3))[0],
        "voice": list(second.subnets(prefixlen_diff=3))[1],
        "mgmt": list(second.subnets(prefixlen_diff=4))[4],
        "special": list(second.subnets(prefixlen_diff=5))[10],
        "loopback": list(second.subnets(prefixlen_diff=5))[11],
    }
    data.update({"subnets": subnets})
    data.update({"telephony_prefix": node["telephony_prefix"]})

    addr = {
        "rtr": {"lb0": subnets["data"][1], "oobm": subnets["mgmt"][1]},
        "dsw": {
            "data_svi10": subnets["data"][-2],
            "biomed_svi20": subnets["biomed"][-2],
            "voice_svi30": subnets["voice"][-2],
            "mgmt_svi40": subnets["mgmt"][-2],
            "special_svi50": subnets["special"][-2],
        },
        "asw1": {"mgmt_svi40": subnets["mgmt"][2]},
        "asw2": {"mgmt_svi40": subnets["mgmt"][3]},
        "asw3": {"mgmt_svi40": subnets["mgmt"][4]},
        "asw4": {"mgmt_svi40": subnets["mgmt"][5]},
        "asw5": {"mgmt_svi40": subnets["mgmt"][6]},
    }
    data.update({"addr": addr})
    return data


if __name__ == "__main__":
    main()
