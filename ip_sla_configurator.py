#!/usr/bin/env python

import sys
from netmiko import ConnectHandler
from dotenv import load_dotenv, find_dotenv


def get_sla_list(working_device):
    output = working_device.send_command("show run | in ip sla [0-9]")
    sla_list = output.split("\n")
    return sla_list


def configure_sla(working_device, sla_number, dst_address, description):
    sla_list = get_sla_list(working_device)
    if sla_number in sla_list:
        sys.exit("SLA number already in use, Please select a new number")
    junk = working_device.send_config_set['ip sla %s' % sla_number, ]
    # TODO: FINISH


def main():
    src_address = None
    dst_address = None
    sla_number = None
    description = None
    # Load env vars
    try:
        load_dotenv(find_dotenv())
        username = os.environ.get("USERNAME")
        password = os.environ.get("PASSWORD")

    except:
        sys.exit("Username and password enviromnent variables are not set. Check .env file.")

    # grab src (device address) from args
    if ("src_address" and "dst_address") not in sys.argv:
        sys.exit("Source and destination IP address not set")
    for arg in sys.argv:
        if "src_address" in arg:
            src_address = arg.split("=")[1]
        if "dst_address" in arg:
            dst_address = arg.split("=")[1]
        if "sla_number" in arg:
            sla_number = arg.split("=")[1]
        if "description" in arg:
            description = arg.split("=")[1]
    if not src_address or not dst_address or not sla_number:
        sys.exit("Source and destination IP address, and SLA number not set")

    device = {'device_type': 'cisco_ios',
              'ip': src_address,
              'username': username,
              'password': password}
    try:
        working_device = ConnectHandler(**device)
    except:
        sys.exit("Please check user and pass environment variables, and source ip address")


if __name__ == "__main__":
    main()