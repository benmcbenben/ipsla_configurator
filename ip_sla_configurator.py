#!/usr/bin/env python

import sys
import os
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
    junk = working_device.send_config_set['ip sla {0}'.format(sla_number),
                                          'icmp-jitter {0} num-packets 100 interval 30'.format(dst_address), 'timeout 500',
                                          'threshold 500',  ' frequency 10',
                                          'history statistics-distribution-interval 100',
                                          'history distributions-of-statistics-kept 20',
                                          'tag {0}'.format(description),
                                          'ip sla schedule {0} life forever start-time now'.format(sla_number)]
    return


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

    print sys.argv
    # grab src (device address) from args
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

    configure_sla(working_device, sla_number, dst_address, description)


if __name__ == "__main__":
    main()
