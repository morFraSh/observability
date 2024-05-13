#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jnpr.junos import Device
from jnpr.junos.exception import *
from pprint import pprint
from lxml import etree
from lxml import html
from jxmlease import parse
from argparse import ArgumentParser, RawTextHelpFormatter
from json import dumps
from re import match, compile


def get_diagnostics_optics_and_descr(host, user_netconf, ssh_key, timeout_a, mode_et_env, mode_sat_a):
    """Used when mode=descr_diag-opt"""
    if mode_et_env == "et-env":
        mode_et_env = True
    elif mode_et_env == "no-et-env":
        mode_et_env = False
    else:
        return "Error mode_et_env"
    if mode_sat_a == "on-sat":
        mode_sat_a = True
    elif mode_sat_a == "no-sat":
        mode_sat_a = False
    else:
        return "Error mode_sat_a"

    json_disc_list = []
    interfaces_descr = {}
    interfaces_lane_et = {}
    interfaces_lane = {}
    ddm_interface_sat = None
    int_et_breakout = compile(r'et.*|xe.*\:\d')
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_a)
    dev.open(auto_probe=timeout_a)
    ddm_interfaces = dev.rpc.get_interface_optics_diagnostics_information()
    if mode_sat_a is True:
        ddm_interface_sat = dev.rpc.show_interface_optics_diagnostics_satellite()
    interface_descr = dev.rpc.get_interface_information(descriptions=True)
    interfaces_status = dev.rpc.get_interface_information(terse=True)
    dev.close()

    ddm_interfaces_lane = ddm_interfaces.xpath('//physical-interface/name | //lane-index')
    ddm_interfaces_xpath = ddm_interfaces.xpath('//physical-interface/name')

    if mode_sat_a is True:
        ddm_interfaces_lane_sat = ddm_interface_sat.xpath('//physical-interface/name | //lane-index')
        ddm_interfaces_sat_xpath = ddm_interface_sat.xpath('//physical-interface/name')
        ddm_interfaces_lane = ddm_interfaces_lane + ddm_interfaces_lane_sat
        ddm_interfaces_xpath = ddm_interfaces_xpath + ddm_interfaces_sat_xpath

    def interface_xpath_operstatus(ddm_interfaces_xpath, interfaces_status):
        name = []
        for prename in ddm_interfaces_xpath:
            prename = (parse
                    (etree.tostring
                     (prename, encoding='unicode')))
            nameint = prename['name']
            if mode_sat_a is True:
                interfaces_diag_na = ddm_interface_sat.xpath(
                    '//physical-interface/name[text()[normalize-space()="{p1}"]]/../optics-diagnostics/optic-diagnostics-not-available[1]'.format(
                        p1=nameint))
            else:
                interfaces_diag_na = ddm_interfaces.xpath(
                    '//physical-interface/name[text()[normalize-space()="{p1}"]]/../optics-diagnostics/optic-diagnostics-not-available[1]'.format(
                        p1=nameint))
            interfaces_status_oper = interfaces_status.xpath(
                '//physical-interface/name[text()[normalize-space()="{p1}"]]/following::oper-status[1]'.format(p1=nameint))
            if not interfaces_diag_na == [] and not interfaces_diag_na is None:
                interfaces_diag_na = False
            else:
                interfaces_diag_na = True
            for status in interfaces_status_oper:
                status = (parse(etree.tostring(status, encoding='unicode')))
                if mode_et_env is True:
                    if interfaces_diag_na is True:
                        if int_et_breakout.match(nameint):
                            if status['oper-status'] == 'up':
                                    name.append(nameint)
                elif mode_et_env is False:
                    if interfaces_diag_na is True:
                        if not int_et_breakout.match(nameint):
                            if status['oper-status'] == 'up':
                                name.append(nameint)
        return name

    name = interface_xpath_operstatus(ddm_interfaces_xpath, interfaces_status)
    if not interface_descr is None:
        for descr in interface_descr:
            descr_name = (parse
                            (etree.tostring
                            (descr.find('.name'))))
            descr_description = (parse
                                 (etree.tostring
                                  (descr.find('.description'))))
            interfaces_descr.update({str(descr_name['name']): str(descr_description['description'])})
    if not ddm_interfaces is None:
        name_int = []
        if mode_et_env is True:
            for lane in ddm_interfaces_lane:

                lane = (parse
                        (etree.tostring
                         (lane, encoding='unicode')))
                if lane.get('name',False) is False:
                    lane_index_list.append(str(lane['lane-index']))

                    if lane_index_list != []:
                        interfaces_lane_et.setdefault(str(name_int),{}).update({'lane-index': lane_index_list})
                else:
                    name_int = lane['name']
                    lane_index_list = []
                    interfaces_lane.update({str(name_int):''})
                if interfaces_lane_et != {}:
                    interfaces_lane.update(interfaces_lane_et)

        for value in name:
            if mode_et_env is True:
                if not interfaces_lane[value] == '':
                    value_et = value
                    lane_list = interfaces_lane[value]['lane-index']
                    for list_l in lane_list:
                        if value_et in interfaces_descr:
                            json_disc_list.append(
                                {'name': str(value_et),
                                'lane_idx': str(list_l),
                                'description': str(interfaces_descr[value_et])})
                        else:
                            json_disc_list.append(
                                {'name': str(value_et),
                                'lane_idx': str(list_l),
                                'description': ''})
            elif mode_et_env is False:
                if value in interfaces_descr:
                    json_disc_list.append(
                        {'name': str(value),
                        'description': str(interfaces_descr[value])})
                else:
                    json_disc_list.append(
                        {'name': str(value),
                        'description': ''})

    return json_disc_list

def get_diagnostics_optics(host, user_netconf, ssh_key, timeout_a, mode_sat_a):
    """Used when mode=diag-opt"""
    if mode_sat_a == "on-sat":
        mode_sat_a = True
    elif mode_sat_a == "no-sat":
        mode_sat_a = False
    else:
        return "Error mode_sat_a"
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_a)

    dev.open()
    ddm_interfaces = dev.rpc.get_aaa_subscriber_table()
    if mode_sat_a is True:
        ddm_interfaces_sat = dev.rpc.show_interface_optics_diagnostics_satellite()
    dev.close()

    if mode_sat_a is True:
        [ddm_interfaces.insert(0, i) for i in ddm_interfaces_sat]

    return etree.tostring(ddm_interfaces, encoding='unicode',method='xml',with_tail=False)

def diag_exception(mode_a):
    try:
        #####selection mode:
        if mode_a == "diag-opt":
            result = get_diagnostics_optics(host_a, user_netconf_a, ssh_key_a, timeout_a, mode_sat_a)
            if not result is None:
                return result
        elif mode_a == "descr_diag-opt":
            result = get_diagnostics_optics_and_descr(host_a, user_netconf_a, ssh_key_a, timeout_a, mode_et_env, mode_sat_a)
            ####json formated####
            result = dumps(result, indent=4, separators=(',', ': '))
            return result
        else:
            return "Error: mode generic"

    except (ConnectRefusedError,
            ConnectUnknownHostError,
            ConnectAuthError) as err:
        return "Error: Equipment name or password wrong, {0}".format(err)
    except (ConnectTimeoutError,
            RpcTimeoutError) as err:
        return 'Error: Timeout(s), {0}'.format(err)
    except ProbeError as err:
        return 'Error: Probe Timeout(s), {0}'.format(err)
    except CommitError as err:
        return 'Error: Commit, {0}'.format(err)
    except ConnectError as err:
         return 'Error: ConnectError, {0}'.format(err)
    except RpcError as err:
         return 'Error: RPC, {0}'.format(err)
    except JSONLoadError as err:
        return 'Error: JsonLoad, {0}'.format(err)



if __name__ == '__main__':
    parser = ArgumentParser(add_help=True,
                            formatter_class=RawTextHelpFormatter,
                            description='Get information on optical trancievers',
                            usage='%(prog)s --host --user --key --timeout --mode --etlane')

    parser.add_argument("--user", "-u", help='username', metavar='')
    parser.add_argument("--key", "-k", help='full path to rsa private key', metavar='')
    parser.add_argument("--host", "-H", help='set host ip address', required=True, metavar='')
    parser.add_argument("--timeout", "-t", help='set host timeout', required=True, metavar='')
    parser.add_argument("--mode", "-m", help='set mode diag-opt or descr_diag-opt', metavar='')
    parser.add_argument("--etlane", "-et", default='no-et-env', help='set et-env or no-et-env', metavar='')
    parser.add_argument("--sat", "-s", default='no-sat', help='on-sat or no-sat', metavar='')
    args = parser.parse_args()

    host_a = args.host
    user_netconf_a = args.user
    ssh_key_a = args.key
    mode_a = args.mode
    timeout_a = int(args.timeout)
    mode_et_env = args.etlane
    mode_sat_a = args.sat

    print(diag_exception(mode_a))
