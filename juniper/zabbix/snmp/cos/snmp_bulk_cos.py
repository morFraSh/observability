#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from pysnmp.hlapi import *
import timeit
import argparse

parser = argparse.ArgumentParser(description='Get information on cos conters interfaces', usage='host user key (interface name)' )

parser.add_argument('host', help='set host address')
parser.add_argument('community', help='set host community')

args = parser.parse_args()



##filter
prefilter = ''
filter_inter = re.compile('^' + prefilter + '$')

snmp_index_list = []
snmp_alias_dict = {}
snmp_name_dict = {}
snmp_name_dict_filter={}


queue_snmp_alias = []
listsnmp_pre_json = []

##
community_bulk = args.community
host_snmp = args.host

oid_cos_con = '.1.3.6.1.4.1.2636.3.15.6.1.11.0'
oid_name_con = '1.3.6.1.2.1.31.1.1.1.1'
oid_alias_com = '.1.3.6.1.2.1.31.1.1.1.18.'

#
snmp_endpoint_name = ""
snmp_endpoint_alias = ""
snmpindex_value = ""

#timer_A = timeit.default_timer()

for (errorIndication,
     errorStatus,
     errorIndex,
     varBinds) in bulkCmd(SnmpEngine(),
                          CommunityData(community_bulk),
                          UdpTransportTarget((host_snmp, 161)),
                          ContextData(),
                          0, 50,
                          ObjectType(
                              ObjectIdentity(oid_cos_con)
                          ),
                          lexicographicMode=False):

    if errorIndication:
        print(errorIndication)
        break
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        break
    else:
        for varBind in varBinds:
            #snmp_endpoint = (' = '.join([x.prettyPrint() for x in varBind]))
            snmpindex_value = snmpindex_value + str(varBind) + ';;;'

snmpindex_value_re = re.finditer(r'2636.3.15.6.1.11.0.(.*?)\s=\s(.*?);;;',snmpindex_value)

for m in snmpindex_value_re:
    ##value != 0
    # if not m.group(2) == '0':
    #     print(m.group(2))
    ############################

    snmp_index_list.append(str(m.group(1)))

for (errorIndication,
     errorStatus,
     errorIndex,
     varBinds) in bulkCmd(SnmpEngine(),
                          CommunityData(community_bulk),
                          UdpTransportTarget((host_snmp, 161)),
                          ContextData(),
                          0, 50,
                          ObjectType(
                              ObjectIdentity(oid_name_con)
                          ),
                          lexicographicMode=False):
    if errorIndication:
        print(errorIndication)
        break
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        break
    else:
        for varBind in varBinds:
            #snmp_endpoint_1 = (' = '.join([x.prettyPrint() for x in varBind]))
            snmp_endpoint_name = snmp_endpoint_name + str(varBind) + ';;;'
            #
snmp_endpoint_name_re = re.finditer(r'31.1.1.1.1.(.*?)\s=\s(.*?);;;',snmp_endpoint_name)

for m1 in snmp_endpoint_name_re:
    snmp_name_dict.update({str(m1.group(1)):str((m1.group(2)))})

for key in snmp_index_list:

    name_snmp_int = snmp_name_dict.get(key)
    name_snmp_int_filter = filter_inter.search(str(name_snmp_int))

    if name_snmp_int_filter == None:
        if not name_snmp_int == None:
            snmp_name_dict_filter.update({key: str(name_snmp_int)})

#

for index_s in snmp_name_dict_filter:
    oid_alias = oid_alias_com + index_s
    queue_snmp_alias.append([ObjectType(ObjectIdentity(oid_alias))])

snmp_alias_get = getCmd(SnmpEngine(),
              CommunityData(community_bulk),
              UdpTransportTarget((host_snmp, 161)),
              ContextData())

next(snmp_alias_get)

while queue_snmp_alias:
    errorIndication, errorStatus, errorIndex, varBinds = snmp_alias_get.send(queue_snmp_alias.pop())
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            snmp_endpoint_alias = snmp_endpoint_alias + str(varBind) + ';;;'
            #print(' = '.join([x.prettyPrint() for x in varBind]))

snmp_endpoint_alias_re = re.finditer(r'31.1.1.1.18.(.*?)\s=\s(.*?);;;', snmp_endpoint_alias)

for ali in snmp_endpoint_alias_re:
    #print(ali.group(1), ": ", ali.group(2))
    snmp_alias_dict.update({str(ali.group(1)): str(ali.group(2))})

for key in snmp_name_dict_filter:
    snmpindex = key
    snmp_name = str(snmp_name_dict_filter[key])
    snmp_alias = str(snmp_alias_dict[key])

    listsnmp_pre_json.append(
         {'{#SNMPINDEX}': snmpindex, '{#IFNAME}': snmp_name,
          '{#IFALIAS}': snmp_alias})

print (json.dumps(listsnmp_pre_json, sort_keys=True, indent=4))

#print(timeit.default_timer() - timer_A)
