import requests
import requests_cache

requests_cache.install_cache('matdb_cache')

BASE_URL = 'https://adsorption.nist.gov/matdb/api'
MATERIALS_API = BASE_URL + '/materials.json'

MATERIALS_JSON = requests.get(MATERIALS_API).json()
MATERIALS_LIST = [ m['name'] for m in MATERIALS_JSON ]
