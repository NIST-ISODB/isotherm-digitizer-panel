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
        'names': [m['name'] for m in json_data],
    }


def find_by_name(name, json):
    """Find JSON corresponding to quantity name."""
    for q_json in json:
        if q_json['name'] == name:
            return q_json

    raise ValueError('JSON for {} not found.'.format(name))
