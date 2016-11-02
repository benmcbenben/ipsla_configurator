#!/usr/bin/env python
"""

Usage:
Add SLA:
 python ip_sla_configurator.py src_address=SOURCE dst_address=DEST sla_number=### -description=DESCRIPTION
Remove SLA:
 python ip_sla_configurator.py src_address=SOURCE sla_number=### -remove

Note: If extra fields are used in "remove" mode, they are ignored

"""
import sys
import os
from netmiko import ConnectHandler
from dotenv import load_dotenv, find_dotenv


def get_sla_list(working_device):
    output = working_device.send_command_expect("show run | in ip sla [0-9]")
    sla_list = output.split("\n")
    return sla_list


def assess_sla(sla_number, working_device):
    sla_list = get_sla_list(working_device)
    for sla in sla_list:
        if str(sla_number) in sla:
            return True
    return False


def configure_sla(working_device, sla_number, dst_address, description):
    if assess_sla(sla_number, working_device):
        sys.exit("SLA number already in use, Please select a new number")

    junk = working_device.send_config_set(['ip sla %s' % sla_number,
                                           'icmp-jitter %s num-packets 100 interval 30' % dst_address, 'timeout 500',
                                           'threshold 500',  ' frequency 10',
                                           'history statistics-distribution-interval 100',
                                           'history distributions-of-statistics-kept 20',
                                           'tag %s' % description,
                                           'ip sla schedule %s life forever start-time now' % sla_number])

    if assess_sla(sla_number, working_device):
        quit("SLA successfully added")
    return


def remove_sla(working_device, sla_number):
    if not assess_sla(sla_number, working_device):
        sys.exit("SLA not found. Please check you have the correct source and SLA number")
    else:
        junk = working_device.send_config_set(['no ip sla %s'])
    if not assess_sla(sla_number, working_device):
        quit("SLA Removal successful")
    return


def main():
    src_address = None
    dst_address = None
    sla_number = None
    description = None
    remove_mode = False
    # Load env vars
    try:
        load_dotenv(find_dotenv())
        username = os.environ.get("USERNAME")
        password = os.environ.get("PASSWORD")

    except:
        sys.exit("Username and password enviromnent variables are not set. Check .env file.")

    # grab src (device address) from args
    if "-remove" in sys.argv:
        remove_mode = True
    for arg in sys.argv:
        if "src_address" in arg:
            src_address = arg.split("=")[1]
        if "dst_address" in arg:
            dst_address = arg.split("=")[1]
        if "sla_number" in arg:
            sla_number = arg.split("=")[1]
        if "description" in arg:
            description = arg.split("=")[1]
    if not src_address:
        sys.exit("Source IP address not set")

    if not dst_address and not remove_mode:
        sys.exit("Destination IP address not set")

    if not sla_number:
        sys.exit("SLA number not set")

    device = {'device_type': 'cisco_ios',
              'ip': src_address,
              'username': username,
              'password': password}
    try:
        working_device = ConnectHandler(**device)
    except:
        sys.exit("Please check user and pass environment variables, and source ip address")

    if not remove_mode:
        configure_sla(working_device, sla_number, dst_address, description)
    else:
        remove_sla(working_device, sla_number)


if __name__ == "__main__":
    main()
