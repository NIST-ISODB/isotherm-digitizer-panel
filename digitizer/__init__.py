# -*- coding: utf-8 -*-
"""Isotherm digitizer for NIST Adsorption Database"""
import os


class ValidationError(ValueError):
    """Error in Form validation."""


MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(MODULE_DIR, 'static')
TEMPLATES_DIR = os.path.join(MODULE_DIR, 'templates')
