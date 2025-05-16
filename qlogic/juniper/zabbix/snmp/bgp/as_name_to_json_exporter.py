#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lxml import html
from json import dumps
from requests import get
from os import chmod
from stat import S_IREAD, S_IRGRP, S_IROTH
from json import load

with open('as-renamed.json','r', encoding='utf-8') as f:
    as_renamed = load(f)

url_as = 'https://bgp.potaroo.net/cidr/autnums.html'
r_as = get(url_as)
json_as_numbs = 'as-numb-name.json'

if r_as.status_code == 200:
    all_data = html.fromstring(r_as.content)

    dick_dict = {}

    for t in all_data.iterfind('.//pre/a'):
        number_as = t.text.strip()
        name_as = t.tail.strip().split(', ')[0]
        if name_as == '-Private Use AS-':
            name_as = 'PrivateAS'
        dick_dict.update({number_as: name_as})

    if as_renamed is not None:
        for a in as_renamed:
            dick_dict.update({a: as_renamed[a]})
    with open(json_as_numbs,'w', encoding='utf-8') as f:
        result = dumps(dick_dict, indent=4, separators=(',', ': '), ensure_ascii=False)
        f.write(result)
    chmod(json_as_numbs, S_IREAD|S_IRGRP|S_IROTH)
else:
    print(r_as.status_code)

