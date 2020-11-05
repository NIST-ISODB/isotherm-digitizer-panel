# -*- coding: utf-8 -*-
"""Setup for NIST Isotherm database digitizer."""

from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name='nist-isotherm-digitizer',
        packages=find_packages(),
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        version='0.1.0',
        description='Isotherm digitizer for the NIST Adsorption Database.',
        author='Leopold Talirz',
        author_email='leopold.talirz@gmail.com',
        #url='to/be/decided',
        install_requires=[
            'panel~=0.10.1',
            'bokeh~=2.3.0.dev5',
            'traitlets~=4.3.3',
            'requests~=2.24.0',
            'requests_cache~=0.5.2',
            'pandas~=1.0.5',
            'pydenticon~=0.3.1',
            #crossrefapi
            #python-dateutil
            #ase
            #manage-crystal
        ],
        extras_require={
            'pre-commit': [
                'pre-commit~=2.2',
                'pylint~=2.6.0',
            ],
            'tests': [
                'pytest~=5.4',
                'pytest-cov~=2.7',
                'coverage<5.0',
            ],
        },
    )
