#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pysnmp.hlapi import *
from json import dumps
#from re import compile, match
from argparse import ArgumentParser



def snmp_walkcmd(community, host_snmp, OID):
    return (next(SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((host_snmp, 161), timeout=5),
                    ContextData(), '0', '20',
                    ObjectType(
                        ObjectIdentity(OID)
                    ),
                    lookupMib=False,
                    lexicographicMode=False
                    ))



def get_interface_info(host_snmp, community, oid, snmpindex_value):

    json_disc_list = []
    one_port_snmp_list = {}
    all_port_dict = {}
    all_snmpvalue_dict = {}
    snmp_index_name = "{#SNMPINDEX}"

    for (errorIndication,
        errorStatus,
        errorIndex,
        varBinds) in snmp_walkcmd(community, host_snmp, oid):
                
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:        
            for varBind in varBinds:
                    
                snmp_index_value = re_oid_snmp.match(str(varBind[0]))
                print (snmp_index_value)
                
                # if snmp_index_value is not None:
                #     snmp_index_value = snmp_index_value.group(1)
                
                # if all_port_dict.get(str(count),False) is False:
                #     all_port_dict.update ({str(count): {int_oid: str(varBind[1]), snmp_index_name: snmp_index_value}})
                # else:
                #     all_port_dict[str(count)].update({int_oid: str(varBind[1]), snmp_index_name: snmp_index_value})
                


    
    # for int_oid in int_oid_dict:
    #     count=0
    #     re_oid_snmp = compile("%s\.(.*)" % int_oid_dict[int_oid])
    #     if int_oid in int_oid_ext_list:
    #         ext_tag = True
    #     for (errorIndication,
    #         errorStatus,
    #         errorIndex,
    #         varBinds) in snmp_walkcmd(community, host_snmp, int_oid_dict[int_oid]):
                    
    #         if errorIndication:
    #             print(errorIndication)
    #             break
    #         elif errorStatus:
    #             print('%s at %s' % (errorStatus.prettyPrint(),
    #                                 errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    #             break
    #         else:        
    #             for varBind in varBinds:
                        
    #                 snmp_index_value = re_oid_snmp.match(str(varBind[0]))
                    
    #                 if snmp_index_value is not None:
    #                     snmp_index_value = snmp_index_value.group(1)
                    
    #                 if all_port_dict.get(str(count),False) is False:
    #                     all_port_dict.update ({str(count): {int_oid: str(varBind[1]), snmp_index_name: snmp_index_value}})
    #                 else:
    #                     all_port_dict[str(count)].update({int_oid: str(varBind[1]), snmp_index_name: snmp_index_value})
                    
    #                 count+=1
    return (all_snmpvalue_dict)



if __name__ == '__main__':
    parser = ArgumentParser(description='Get information FC interfaces', usage='host user key (interface name)' )
    parser.add_argument('--host',"-H", help='set host address', required=True, metavar='')
    parser.add_argument('--community', "-c", help='set host community', required=True, metavar='')
    parser.add_argument('--oid', "-o", help='set oid number', required=True, metavar='')
    args = parser.parse_args()
    
    community = args.community
    host_snmp = args.host
    oid = args.host
    
    snmpindex_value = ""
    
    
    all_snmpvalue_dict = get_interface_info (host_snmp, community, oid, snmpindex_value)

    result = dumps(list(all_snmpvalue_dict.values()), indent=4, separators=(',', ': '))
    print (result)