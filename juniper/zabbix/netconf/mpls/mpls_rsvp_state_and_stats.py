#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jnpr.junos import Device
import jnpr.junos.exception
from lxml import etree
import jxmlease.xmlparser
import argparse
import json.decoder


parser = argparse.ArgumentParser(add_help = True,
                                 formatter_class = argparse.RawTextHelpFormatter,
                                 description = 'Get information on optical trancievers',
                                 usage = '%(prog)s --host --user --key --timeout --output')

parser.add_argument("--user", "-u", help='username', metavar='')
parser.add_argument("--key", "-k", help='full path to rsa private key', metavar='')
parser.add_argument("--host", "-H", help='set host ip address', required=True, metavar='')
parser.add_argument("--timeout", "-t", help='set host timeout', metavar='')
parser.add_argument("--statistics", "-s", help='activate ingress statistics mode ', action='store_true')
parser.add_argument("--transit_lsp", "-T", help='activate transit statistics mode (all_mode active all lsp)', default='deactivate' , metavar='')
parser.add_argument("--output", "-o", help='set mode lld_set or elem_set', metavar='')
args = parser.parse_args()

host_a = args.host
user_netconf_a = args.user
ssh_key_a = args.key
timeout_a = args.timeout
transit_lsp_a = args.transit_lsp
statistics_a = args.statistics
output_a = args.output


def get_mpls_lsp_ingress_lld(host, user_netconf, ssh_key, timeout_rpc, transit_lsp):
    """Used when mode=descr lld_set"""
    json_disc_list = []
    lsp_name_descr = {}
    lsp_name = []
    param_set = []
    param_ingress = True
    param_transit = False

    if transit_lsp == 'trans_mode':
        param_set.append('t')
    elif transit_lsp == 'all_mode':
        param_set.append('a')

    if 't' in param_set:
        param_transit = True
        param_ingress = False
    elif 'a' in param_set:
        param_transit = False
        param_ingress = False

    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_rpc)
    dev.open()
    mpls_lsp_all = dev.rpc.get_mpls_lsp_information(ingress=param_ingress, transit=param_transit)
    dev.close()

    mpls_lsp_name = mpls_lsp_all.xpath('(//rsvp-session|//mpls-lsp)/name')
    #print(mpls_lsp_name)

    if not mpls_lsp_all == None:
        if not mpls_lsp_name == None:
            for name in mpls_lsp_name:
                name = (jxmlease.parse
                        (etree.tostring
                         (name, encoding='unicode')))

                name_l = name['name']
                lsp_name.append(str(name_l))

                lsp_description = mpls_lsp_all.xpath('(//rsvp-session|//mpls-lsp)/name[text()[normalize-space()="%s"]]/following::lsp-description[1]' % name_l)

                for descr in lsp_description:

                    # print(lsp_name)
                    # print(name_l)
                    descr = (jxmlease.parse
                             (etree.tostring
                              (descr, encoding='unicode')))
                    lsp_name_descr.update({str(name_l): str(descr['lsp-description'])})

            for value in lsp_name:
                json_disc_list.append(
                    {'name': str(value),
                    'description': str(lsp_name_descr.get(value, ''))})

    return json_disc_list


def get_mpls_lsp_ingress_elem(host, user_netconf, ssh_key, timeout_rpc, transit_lsp, stat_mode):
    """Used when mode=descr elem_set"""
    param_set = []
    param_ingress = True
    param_transit = False
    param_statistics = False
    
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_rpc)

    if transit_lsp == 'trans_mode':
        param_set.append('t')
    elif transit_lsp == 'all_mode':
        param_set.append('a')
    # if stat_mode is True:
    #     param_set.append('s')

    if 't' in param_set:
        param_transit = True
        param_ingress = False
    elif 'a' in param_set:
        param_transit = False
        param_ingress = False

    dev.open()
    mpls_lsp_all = dev.rpc.get_mpls_lsp_information(ingress=param_ingress, transit=param_transit, statistics=stat_mode)
    dev.close()
    mpls_lsp_all = etree.tostring(mpls_lsp_all, encoding='unicode')
    return mpls_lsp_all


def mpls_lsp_exception(mode):
    try:
        #####selection mode:
        if mode == "elem_set":
            result = get_mpls_lsp_ingress_elem(host_a, user_netconf_a, ssh_key_a, timeout_a, transit_lsp_a, statistics_a)
            if not result == None:
                return result
        elif mode == "lld_set":
            result = get_mpls_lsp_ingress_lld(host_a, user_netconf_a, ssh_key_a, timeout_a, transit_lsp_a)
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
    except jnpr.junos.exception.RpcError as err_2:
        print('Error: RPC')
        return err_2


if __name__ == '__main__':
    print(mpls_lsp_exception(output_a))

