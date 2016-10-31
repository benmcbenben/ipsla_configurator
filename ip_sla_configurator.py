#!/usr/bin/env python


from netmiko import ConnectHandler
from dotenv import load_dotenv, find_dotenv


def get_sla_list(source_interface, working_device):
    output = working_device.send_command("show run interface %s" % source_interface)
    output = output.split("\n")
    parsed_output = CiscoConfParse(output)
    interface = parsed_output.find_objects(r'^interface')[0]
    return interface


def main():
    src_address = None
    dst_address = None
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
    if not src_address or not dst_address:
        sys.exit("Source and destination IP address not set")

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