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
parser.add_argument("--transit_lsp", "-t", help='activate all stattistic mode ',default='deactivate' , metavar='')
parser.add_argument("--output", "-o", help='set mode lld_set or elem_set', metavar='')
args = parser.parse_args()

host_a = args.host
user_netconf_a = args.user
ssh_key_a = args.key
timeout_a = args.timeout
output_a = args.output
transit_lsp_a = args.transit_lsp

def get_mpls_lsp_ingress_lld(host, user_netconf, ssh_key, timeout_rpc):
    """Used when mode=descr lld_set"""

    json_disc_list = []
    lsp_name_descr = {}
    lsp_name = []

    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_rpc)
    dev.open()
    mpls_lsp_all = dev.rpc.get_mpls_lsp_information(ingress=, statistics=True)
    dev.close()

    mpls_lsp_name = mpls_lsp_all.xpath('//mpls-lsp/name')

    if not mpls_lsp_all == None:
        if not mpls_lsp_name == None:
            for name in mpls_lsp_name:
                name = (jxmlease.parse
                        (etree.tostring
                         (name, encoding='unicode')))
                name_l = name['name']
                lsp_description = mpls_lsp_all.xpath(
                    '//mpls-lsp/name[text()[normalize-space()="%s"]]/following::lsp-description[1]' % name_l)

                for descr in lsp_description:
                    lsp_name.append(str(name_l))
                    descr = (jxmlease.parse
                             (etree.tostring
                              (descr, encoding='unicode')))
                    lsp_name_descr.update({str(name_l): str(descr['lsp-description'])})

            for value in lsp_name:
                json_disc_list.append(
                    {'name': str(value),
                    'description': str(lsp_name_descr[value])})

    return json_disc_list


def get_mpls_lsp_ingress_elem(host, user_netconf, ssh_key, timeout_rpc):
    """Used when mode=descr elem_set"""
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_rpc)

    dev.open()
    mpls_lsp_ingress = dev.rpc.get_mpls_lsp_information(ingress=True, statistics=True)
    dev.close()
    mpls_lsp_ingress = etree.tostring(mpls_lsp_ingress, encoding='unicode')
    return mpls_lsp_ingress


def mpls_lsp_exception(mode, full_out):
    try:
        #####selection mode:
        if full_out == "deactivate":
            transit_lsp = 
        if mode == "elem_set":
            result = get_mpls_lsp_ingress_elem(host_a, user_netconf_a, ssh_key_a, timeout_a)
            if not result == None:
                return result
        elif mode == "lld_set":
            result = get_mpls_lsp_ingress_lld(host_a, user_netconf_a, ssh_key_a, timeout_a)
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
    print(mpls_lsp_exception(output_a, transit_lsp_a))

