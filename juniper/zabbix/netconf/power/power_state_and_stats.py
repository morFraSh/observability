#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jnpr.junos import Device
import jnpr.junos.exception
from lxml import etree
#import jxmlease.xmlparser
import argparse
#import json.decoder


parser = argparse.ArgumentParser(add_help = True,
                                 formatter_class = argparse.RawTextHelpFormatter,
                                 description = 'Get information on optical trancievers',
                                 usage = '%(prog)s --host --user --key --timeout --output')

parser.add_argument("--user", "-u", help='username', metavar='')
parser.add_argument("--key", "-k", help='full path to rsa private key', metavar='')
parser.add_argument("--host", "-H", help='set host ip address', required=True, metavar='')
parser.add_argument("--timeout", "-t", help='set host timeout', metavar='')
args = parser.parse_args()

host_a = args.host
user_netconf_a = args.user
ssh_key_a = args.key
timeout_a = args.timeout



def get_environment_component_information_lld(host, user_netconf, ssh_key, timeout_rpc):
    """Used when mode=descr lld_set"""
    json_disc_list = []

    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_rpc)
    dev.open()
    env_power_all = dev.rpc.get_environment_pem_information()
    dev.close()

    return etree.tostring(env_power_all, encoding='unicode')



def power_exception():
    try:
        result = get_environment_component_information_lld(host_a, user_netconf_a, ssh_key_a, timeout_a)
        if not result == None:
            return result

    except (jnpr.junos.exception.ConnectRefusedError,
            jnpr.junos.exception.ConnectUnknownHostError,
            jnpr.junos.exception.ConnectAuthError) as err:
        print("Equipment name or password wrong.")
        return err
    except (jnpr.junos.exception.ConnectTimeoutError,
            jnpr.junos.exception.RpcTimeoutError) as err_1:
        print('Error: Timeout')
        return err_1
    except jnpr.junos.exception.RpcError as err_2:
        print('Error: RPC')
        return err_2


if __name__ == '__main__':
    print(power_exception())

