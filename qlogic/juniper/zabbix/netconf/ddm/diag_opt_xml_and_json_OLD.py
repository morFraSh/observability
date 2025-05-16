#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jnpr.junos import Device
import jnpr.junos.exception
from pprint import pprint
from lxml import etree
from lxml import html
import jxmlease
import argparse
import json

parser = argparse.ArgumentParser(add_help=True,
                                 formatter_class=argparse.RawTextHelpFormatter,
                                 description='Get information on optical trancievers',
                                 usage='%(prog)s --host --user --key --timeout --mode --etlane' )

parser.add_argument("--user","-u", help='username', metavar='')
parser.add_argument("--key","-k", help='full path to rsa private key', metavar='')
parser.add_argument("--host","-H", help='set host ip address', required=True, metavar='')
parser.add_argument("--timeout","-t",help='set host timeout', metavar='')
parser.add_argument("--mode","-m", help='set mode diag-opt or descr_diag-opt', metavar='')
parser.add_argument("--etlane","-et", default='no-et-env', help='set et-env or no-et-env', metavar='')
args = parser.parse_args()

host_a = args.host
user_netconf_a = args.user
ssh_key_a = args.key
mode_a = args.mode
timeout_a = args.timeout
mode_et_env = args.etlane

def get_diagnostics_optics_and_descr(host, user_netconf, ssh_key, timeout_a, mode_et_env):
    """Used when mode=descr_diag-opt"""
    if mode_et_env == "et-env":
        mode_et_env = True
    elif mode_et_env == "no-et-env":
        mode_et_env = False
    else:
        return "Error mode_et_env"

    json_disc_list = []
    interfaces_descr = {}
    interfaces_lane_et = {}
    interfaces_lane = {}
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_a)
    dev.open()
    ddm_interfaces = dev.rpc.get_interface_optics_diagnostics_information()
    interface_descr = dev.rpc.get_interface_information(descriptions=True)
    interfaces_status = dev.rpc.get_interface_information(terse=True)
    dev.close()

    ddm_interfaces_lane = ddm_interfaces.xpath('//physical-interface/name | //lane-index')
    ddm_interfaces_xpath = ddm_interfaces.xpath('//physical-interface/name')
    #print(etree.tostring(interfaces_status, encoding='unicode'))
    def interface_xpath_operstatus(ddm_interfaces_xpath, interfaces_status):
        name=[]
        for prename in ddm_interfaces_xpath:
            prename = (jxmlease.parse
                    (etree.tostring
                     (prename, encoding='unicode')))
            nameint = prename['name']
            interfaces_status_oper = interfaces_status.xpath(
                '//physical-interface/name[text()[normalize-space()="%s"]]/following::oper-status[1]' % nameint)
            for status in interfaces_status_oper:
                status = (jxmlease.parse(etree.tostring(status, encoding='unicode')))
                if status['oper-status'] == 'up':
                    name.append(nameint)
        return name

    if not interface_descr == None:
        for descr in interface_descr:
            descr_name = (jxmlease.parse
                            (etree.tostring
                            (descr.find('.name'))))
            descr_description = (jxmlease.parse
                                 (etree.tostring
                                  (descr.find('.description'))))
            interfaces_descr.update({str(descr_name['name']): str(descr_description['description'])})
    if not ddm_interfaces == None:
        name_int = []
        if mode_et_env == True:
            for lane in ddm_interfaces_lane:

                lane = (jxmlease.parse
                        (etree.tostring
                         (lane, encoding='unicode')))
                if lane.get('name',False) == False:
                    lane_index_list.append(str(lane['lane-index']))

                    if lane_index_list != []:
                        interfaces_lane_et.setdefault(str(name_int),{}).update({'lane-index': lane_index_list})
                else:
                    name_int = lane['name']
                    lane_index_list = []
                    interfaces_lane.update({str(name_int):''})
                if interfaces_lane_et != {}:
                    interfaces_lane.update(interfaces_lane_et)

        name = interface_xpath_operstatus(ddm_interfaces_xpath, interfaces_status)

        for value in name:
            if mode_et_env == True:
                if not interfaces_lane[value] == '':
                    value_et = value
                    lane_list = interfaces_lane[value]['lane-index']
                    for list in lane_list:
                        if value_et in interfaces_descr:
                            json_disc_list.append(
                                {'name': str(value_et),
                                'lane_idx': str(list),
                                'description': str(interfaces_descr[value_et])})
                        else:
                            json_disc_list.append(
                                {'name': str(value_et),
                                'lane_idx': str(list),
                                'description': ''})
            elif mode_et_env == False:
                if value in interfaces_descr:
                    json_disc_list.append(
                        {'name': str(value),
                        'description': str(interfaces_descr[value])})
                else:
                    json_disc_list.append(
                        {'name': str(value),
                        'description': ''})

    return json_disc_list

def get_diagnostics_optics(host, user_netconf, ssh_key, timeout_a):
    """Used when mode=diag-opt"""
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_a)

    dev.open()
    ddm_interfaces = dev.rpc.get_interface_optics_diagnostics_information()
    dev.close()
    ddm_interfaces = etree.tostring(ddm_interfaces, encoding='unicode')
    return ddm_interfaces

def diag_exception(mode_a):
    try:
        #####selection mode:
        if mode_a == "diag-opt":
            result = get_diagnostics_optics(host_a, user_netconf_a, ssh_key_a, timeout_a)
            if not result == None:
                return result
        elif mode_a == "descr_diag-opt":
            result = get_diagnostics_optics_and_descr(host_a, user_netconf_a, ssh_key_a, timeout_a, mode_et_env)
            ####json formated####
            result = json.dumps(result, indent=4, separators=(',', ': '))
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
    except (jnpr.junos.exception.RpcError) as err_2:
        print('Error: RPC')
        return err_2

if __name__ == '__main__':
    print(diag_exception(mode_a))
