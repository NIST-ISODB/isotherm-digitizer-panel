# -*- coding: utf-8 -*-
"""
Configuration, including options fetched from ISDB API.
"""
import requests
import requests_cache

requests_cache.install_cache('matdb_cache')

BASE_URL = 'https://adsorption.nist.gov/isodb/api'

QUANTITY_API_MAPPING = {
    'adsorbents': '/materials.json',
    'adsorbates': '/gases.json',
    'isotherm_type': '/isotherm-type-lookup.json',
    'pressure_units': '/pressure-unit-lookup.json',
    'adsorption_units': '/adsorption-unit-lookup.json',
    'measurement_type': '/category-type-lookup.json',
    'concentration_units': '/concentration-unit-lookup.json',
    'composition_type': '/composition-type-lookup.json',
}

QUANTITIES = {}
for quantity, url in QUANTITY_API_MAPPING.items():
    json_data = requests.get(BASE_URL + url).json()
    QUANTITIES[quantity] = {
        'json': json_data,
        'names': ['Select'] + [m['name'] for m in json_data],
    }

QUANTITIES['isotherm_type']['names'].append('Not specified')


def find_by_name(name, json):
    """Find JSON corresponding to quantity name."""
    for q_json in json:
        if q_json['name'] == name:
            return q_json

    raise ValueError('JSON for {} not found.'.format(name))

SINGLE_COMPONENT_EXAMPLE = \
"""#pressure,adsorption
0.310676,0.019531
5.13617,0.000625751
7.93711,0.0204602
12.4495,0.06066
30.0339,0.159605
44.8187,0.200392
58.3573,0.270268
66.2941,0.300474
72.9855,0.340276"""

MULTI_COMPONENT_EXAMPLE = \
"""#pressure,composition1,adsorption1,...,total_adsorption(opt)
0.310676,1,0.019531,0.019531
5.13617,1,0.000625751,0.000625751
7.93711,1,0.0204602,0.0204602
12.4495,1,0.06066,0.06066
30.0339,1,0.159605,0.159605
44.8187,1,0.200392,0.200392
58.3573,1,0.270268,0.270268
66.2941,1,0.300474,0.300474
72.9855,1,0.340276,0.340276"""
