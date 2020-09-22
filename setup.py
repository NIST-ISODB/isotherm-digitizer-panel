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
            #'bokeh~=2.1',
            #'panel~=0.9',
            'requests',
            'requests_cache',
            'pandas~=1.0.5',
            #ipython
            #notebook
            #crossrefapi
            #python-dateutil
            #ase
            #manage-crystal #by danieleongari
        ],
        extras_require={
            'pre-commit': [
                'pre-commit~=2.2',
                'pylint~=2.5.0',
            ],
            'tests': [
                'pytest~=5.4',
                'pytest-cov~=2.7',
                'coverage<5.0',
            ],
        },
    )
