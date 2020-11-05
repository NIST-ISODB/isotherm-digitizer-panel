# -*- coding: utf-8 -*-
"""Isotherm digitizer for NIST Adsorption Database"""
import os
from bokeh import __version__ as bk_ver


class ValidationError(ValueError):
    """Error in Form validation."""


MODULE_DIR = os.path.dirname(os.path.realpath(__file__))

# TODO: Remove after official bokeh/panel release  # pylint: disable=fixme
if bk_ver.startswith('2.3'):
    restrict_kwargs = {'restrict': False}
else:
    restrict_kwargs = {}
