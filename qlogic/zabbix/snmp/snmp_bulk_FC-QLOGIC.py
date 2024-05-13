#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pysnmp.hlapi import *
from json import dumps
from re import compile, match
from argparse import ArgumentParser



def snmp_walkcmd(community_bulk, host_snmp, OID):
    return (bulkCmd(SnmpEngine(),
                    CommunityData(community_bulk),
                    UdpTransportTarget((host_snmp, 161), timeout=5),
                    ContextData(), '0', '20',
                    ObjectType(
                        ObjectIdentity(OID)
                    ),
                    lookupMib=False,
                    lexicographicMode=False
                    ))



def get_interface_info(int_oid_dict, snmpindex_value, int_oid, int_oid_ext_list):

    json_disc_list = []
    one_port_snmp_list = {}
    all_port_dict = {}
    snmp_index_name = "{#SNMPINDEX}"
    ext_tag = False
    
    for int_oid in int_oid_dict:
        count=0
        re_oid_snmp = compile("%s\.(.*)" % int_oid_dict[int_oid])
        if int_oid in int_oid_ext_list:
            ext_tag = True
        for (errorIndication,
            errorStatus,
            errorIndex,
            varBinds) in snmp_walkcmd(community_bulk, host_snmp, int_oid_dict[int_oid]):
                    
            if errorIndication:
                print(errorIndication)
                break
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                break
            else:        
                for varBind in varBinds:
                    
                    if ext_tag is True:
                        snmp_index_name = "{#SNMPINDEXEXT}"
                        
                    snmp_index_value = re_oid_snmp.match(str(varBind[0]))
                    if snmp_index_value is not None:
                        snmp_index_value = snmp_index_value.group(1)
                    
                    if all_port_dict.get(str(count),False) is False:
                        all_port_dict.update ({str(count): {int_oid: str(varBind[1]), snmp_index_name: snmp_index_value}})
                    else:
                        all_port_dict[str(count)].update({int_oid: str(varBind[1]), snmp_index_name: snmp_index_value})
                    
                    count+=1
    return (all_port_dict)



if __name__ == '__main__':
    parser = ArgumentParser(description='Get information FC interfaces', usage='host user key (interface name)' )
    parser.add_argument('--host',"-H", help='set host address')
    parser.add_argument('--community', "-c", help='set host community')
    args = parser.parse_args()
    
    community_bulk = args.community
    host_snmp = args.host
    
    snmpindex_value = ""
    
    int_oid_dict = {"{#FCFXOPERMODE}": "1.3.6.1.2.1.75.1.2.1.1.3",
                    "{#FCFXADMINSTATUS}": "1.3.6.1.2.1.75.1.2.2.1.1",
                    "{#FCFXOPERSTATUS}": "1.3.6.1.2.1.75.1.2.2.1.2",
                    "{#FCFXALIAS}": "1.3.6.1.3.94.1.10.1.17.16.0.0.192.221.52",
                    "{#FCFXNAME}": "1.3.6.1.3.94.1.10.1.18.16.0.0.192.221.52"}
    int_oid_ext_list = ['{#FCFXALIAS}','{#FCFXNAME}']
    
    all_port_dict = get_interface_info (int_oid_dict, snmpindex_value, snmpindex_value, int_oid_ext_list)

    result = dumps(list(all_port_dict.values()), indent=4, separators=(',', ': '))
    print (result)