# -*- coding: utf-8 -*-
"""Test parsing functionality."""
import os
import glob
import json
import pytest

from digitizer.parse import parse_isotherm_data

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(THIS_DIR, 'static')
ISOTHERM_DATA_FILES = glob.glob(os.path.join(STATIC_DIR,
                                             'isotherm_data_*.dat'))

with open(os.path.join(STATIC_DIR, 'isotherm_data.json')) as _handle:
    ISOTHERM_DATA_DICT = json.load(_handle)

ADSORBATES_DICT = [{
    'InChIKey': 'VNWKTOKETHGBQD-UHFFFAOYSA-N',
    'name': 'Methane'
}]


@pytest.mark.parametrize('filename', ISOTHERM_DATA_FILES)
def test_parse_isotherm_data(filename):
    """Test that common input formats are parsed correctly."""
    with open(filename, 'r') as handle:
        data = handle.read()

        parsed = parse_isotherm_data(data,
                                     ADSORBATES_DICT,
                                     form_type='single-component')
        assert parsed == ISOTHERM_DATA_DICT
