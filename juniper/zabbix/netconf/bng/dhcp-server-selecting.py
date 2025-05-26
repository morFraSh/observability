#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jnpr.junos import Device
from jnpr.junos.exception import *
from pprint import pprint
from lxml import etree
from lxml import html
from argparse import ArgumentParser, RawTextHelpFormatter
from json import dumps
from re import match, compile
from pyzabbix.api import ZabbixAPI, ZabbixAPIException
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader




def get_dhcp_bining (host, user_netconf, ssh_key, timeout_a):
    dev = Device(host=host, user=user_netconf, ssh_private_key_file=ssh_key, gather_facts=False, timeout=timeout_a)
    dev.open()
    dhcp_binding = dev.rpc.get_dhcp_server_binding_information()
    dev.close()
    return dhcp_binding



def get_zabbix_history_last(itemid_selecting, zabi_usr, zabi_psw):
    zapi.login(zabi_usr, zabi_psw)
    try:
        last_data = zapi.history.get(output='extend',
                                  itemids=tuple([itemid_selecting]),
                                  history='4',
                                  limit='100',
                                  sortfield="clock",
                                  sortorder="DESC")
    except ZabbixAPIException as e:
        print(e)
        sys.exit()

    if not last_data == []:
        return last_data
    else:
        return ''



def get_zabbix_itemid(hostname_a, zabi_usr, zabi_psw, name_element):
    zapi.login(zabi_usr, zabi_psw)
    try:
        hostid = zapi.host.get(output=['hostid', 'host'],
                                filter={'host': hostname_a})
        itemid_selecting = zapi.item.get(output=['hostid', 'itemid'],
                                  hostids=hostid[0]['hostid'],
                                  search={'name': name_element},
                                  sortfield="name")

    except ZabbixAPIException as e:
        print(e)
        sys.exit()
    if not itemid_selecting == []:
        return itemid_selecting[0]['itemid']
    else:
        return None


def diag_exception():
    try:
        #####selection mode:
        result_list = get_dhcp_bining(host_a, user_netconf_a, ssh_key_a, timeout_a)
        result = '\n'
        selecting_list = ['SELECTING', 'Selecting', 'selecting']
        itemid_selecting = get_zabbix_itemid(hostname_a, zabi_usr, zabi_psw, name_elem_a)
        if not itemid_selecting is None:
            check_to_history = get_zabbix_history_last(itemid_selecting, zabi_usr, zabi_psw)
        else:
            return ''

        for selecting in result_list.iterfind('.//dhcp-binding'):
           if selecting.find('.//lease-state').text in selecting_list:
               lease_exp = selecting.find('.//lease-expires').text
               lease_ip = selecting.find('.//allocated-address').text
               lease_mac = selecting.find('.//mac-address').text
               if int(lease_exp) < 0:
                   for check_elem in check_to_history:
                       if re.search(((r'IP\:\s{p1}\,').format(p1=lease_ip)), check_elem['value']):
                           return result
                   result = result + 'IP: ' + lease_ip + ', MAC: ' + lease_mac + ', Истекает(с): ' + lease_exp + '\n'
        return result

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
                            description='Get information on internal dhcp server',
                            usage='%(prog)s --host --user --key --timeout')

    parser.add_argument("--user", "-u", help='username', metavar='')
    parser.add_argument("--key", "-k", help='full path to rsa private key', metavar='')
    parser.add_argument("--host", "-H", help='set host ip address', required=True, metavar='')
    parser.add_argument("--timeout", "-t", help='set host timeout', required=True, metavar='')
    parser.add_argument("--name_elem", "-e", help='set host name_elem', required=True, metavar='')
    parser.add_argument("--hostname", "-n", help='set hostname', required=True, metavar='')
    parser.add_argument("--zabbix_username", "-zn", help='set zabbix username api', required=True, metavar='')
    parser.add_argument("--zabbix_password", "-zp", help='set zabbix pswd. api', required=True, metavar='')
    parser.add_argument("--zabbix_url", "-zu", help='set zabbix url api', required=True, metavar='')
    args = parser.parse_args()

    host_a = args.host
    user_netconf_a = args.user
    ssh_key_a = args.key
    timeout_a = int(args.timeout)
    name_elem_a = args.name_elem
    hostname_a = args.hostname
    zabi_usr = args.zabbix_username
    zabi_psw = args.zabbix_password
    zabi_url = args.zabbix_url
    
    zapi = ZabbixAPI(zabi_url)

    print(diag_exception())