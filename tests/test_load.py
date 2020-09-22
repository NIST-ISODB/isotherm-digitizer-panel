# -*- coding: utf-8 -*-
"""Test loading data from an isotherm JSON file."""
import os
import glob
import json
import pytest

from digitizer.load_json import load_isotherm_json
from digitizer.forms import IsothermSingleComponentForm
from . import STATIC_DIR

SAMPLE_ISOTHERMS = glob.glob(os.path.join(STATIC_DIR, '*.json'))


@pytest.mark.parametrize('filename', SAMPLE_ISOTHERMS)
def test_load_isotherm_json(filename):
    """Test that common input formats are parsed correctly."""
    json_string = open(filename, 'r').read()
    form = IsothermSingleComponentForm(plot=None, tabs=None)
    load_isotherm_json(form=form, json_string=json_string)

    json_dict = json.loads(json_string)
    assert form.inp_source_type.value == json_dict['articleSource']
