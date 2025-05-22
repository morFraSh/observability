#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jnpr.junos import Device
import jnpr.junos.exception
from lxml import etree
#from lxml import html
#import jxmlease.xmlparser
from argparse import ArgumentParser, RawTextHelpFormatter
#import json.decoder
from json import dumps



def get_environment_component_information_lld(host, user_netconf, ssh_key, timeout_rpc, mode_sat_a):
    """Used when mode=elem_set"""
    
    if mode_sat_a == "on-sat":
        mode_sat_a = True
    elif mode_sat_a == "no-sat":
        mode_sat_a = False
    else:
        return "Error mode_sat_a"
    
    env_power_all_sat = None
    json_lld_list = []
    
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_rpc)
    dev.open()
    env_power_all = dev.rpc.get_environment_pem_information()
    if mode_sat_a is True:
        env_power_all_sat = dev.rpc.get_chassis_environment_pem_satellite_info()
    dev.close()

    env_power_xpath_name = env_power_all.xpath('//environment-component-item[dc-information/dc-detail/dc-power]/name | //environment-component-item[dc-information/dc-detail/str-dc-power]/name')

    if mode_sat_a is True:
        env_power_sat_xpath_name = env_power_all_sat.xpath('//environment-component-item[dc-information/dc-detail/dc-power]/name | //environment-component-item[dc-information/dc-detail/str-dc-power]/name')
        env_power_xpath_name = env_power_xpath_name + env_power_sat_xpath_name
    for psu_name in env_power_xpath_name:
        json_lld_list.append({'name': str(psu_name)})

    return json_lld_list



def get_environment_component_information_elem(host, user_netconf, ssh_key, timeout_rpc, mode_sat_a):
    """Used when mode=lld_set"""
    if mode_sat_a == "on-sat":
        mode_sat_a = True
    elif mode_sat_a == "no-sat":
        mode_sat_a = False
    else:
        return "Error mode_sat_a"
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_rpc)

    dev.open()
    env_power_all = dev.rpc.get_environment_pem_information()
    if mode_sat_a is True:
        env_power_sat = dev.rpc.get_chassis_environment_pem_satellite_info()
    dev.close()

    if mode_sat_a is True:
        [env_power_all.insert(0, i) for i in env_power_sat]

    return etree.tostring(env_power_all, encoding='unicode',method='xml',with_tail=False)



def power_exception(mode):
    try:
        if mode == "elem_set":
            result = get_environment_component_information_elem(host_a, user_netconf_a, ssh_key_a, timeout_rpc, mode_sat_a)
            if not result == None:
                return result
        elif mode == "lld_set":
            result = get_environment_component_information_lld(host_a, user_netconf_a, ssh_key_a, timeout_rpc, mode_sat_a)
            ####json formated####
            result = dumps(result, indent=4, separators=(',', ': '))
            return result
        else:
            return "Error: mode generic"


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
    parser = ArgumentParser(add_help = True,
                                    formatter_class = RawTextHelpFormatter,
                                    description = 'Get information on optical trancievers',
                                    usage = '%(prog)s --host --user --key --timeout --output')

    parser.add_argument("--user", "-u", help='username', metavar='')
    parser.add_argument("--key", "-k", help='full path to rsa private key', metavar='')
    parser.add_argument("--host", "-H", help='set host ip address', required=True, metavar='')
    parser.add_argument("--timeout", "-t", help='set host timeout', metavar='')
    parser.add_argument("--sat", "-s", default='no-sat', help='on-sat or no-sat', metavar='')
    parser.add_argument("--output", "-o", help='set mode lld_set or elem_set', metavar='')
    args = parser.parse_args()

    host_a = args.host
    user_netconf_a = args.user
    ssh_key_a = args.key
    timeout_rpc = args.timeout
    mode_sat_a = args.sat
    output_a = args.output

    print(power_exception(output_a))