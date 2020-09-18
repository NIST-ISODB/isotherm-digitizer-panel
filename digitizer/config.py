# -*- coding: utf-8 -*-
"""
Configuration, including options fetched from ISDB API.
"""
import os
import requests
import requests_cache
from . import MODULE_DIR

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

    names = []
    for m in json_data:
        names.append(m['name'])
        try:
            names += m['synonyms']
        except KeyError:
            pass
    QUANTITIES[quantity] = {
        'json': json_data,
        'names': names,
    }

QUANTITIES['isotherm_type']['names'].append('Not specified')

BIBLIOGRAPHY = requests.get(BASE_URL + '/biblios.json').json()
DOIs = {entry['DOI'] for entry in BIBLIOGRAPHY}


def find_by_name(name, json):
    """Find JSON corresponding to quantity name."""
    for q_json in json:
        try:
            candidates = [q_json['name']] + q_json['synonyms']
        except AttributeError:
            candidates = [q_json['name']]
        if name in candidates:
            return q_json

    raise ValueError('JSON for {} not found.'.format(name))


def find_by_key(keyvalue, keytype, json):
    """Find JSON corresponding to quantity key."""
    for q_json in json:
        try:
            if keyvalue == q_json[keytype]:
                return q_json
        except AttributeError:
            continue

    raise ValueError('JSON for {} not found.'.format(keyvalue))

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

FIGURE_FILENAME_EXAMPLE = 'Figure_S5a.png'
with open(os.path.join(MODULE_DIR, 'static', FIGURE_FILENAME_EXAMPLE),
          'rb') as handle:
    FIGURE_EXAMPLE = handle.read()

SUBMISSION_FOLDER = os.getenv(
    'DIGITIZER_SUBMISSION_FOLDER',
    os.path.join(MODULE_DIR, os.pardir, 'submissions'))
