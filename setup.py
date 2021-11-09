# -*- coding: utf-8 -*-
"""Setup for NIST Isotherm database digitizer."""

from setuptools import setup, find_packages

if __name__ == '__main__':
    with open('README.md', encoding='utf8') as handle:
        setup(
            name='nist-isotherm-digitizer',
            packages=find_packages(),
            long_description=handle.read(),
            long_description_content_type='text/markdown',
            version='0.1.0',
            description='Isotherm digitizer for the NIST Adsorption Database.',
            author='Leopold Talirz',
            author_email='leopold.talirz@gmail.com',
            #url='to/be/decided',
            install_requires=[
                'panel~=0.12.4',
                'bokeh~=2.4.1',
                'traitlets~=5.1.1',
                'requests~=2.26.0',
                'requests_cache~=0.8.1',
                'pandas~=1.3.4',
                'pydenticon~=0.3.1',
                #crossrefapi
                #python-dateutil
                #ase
                #manage-crystal
            ],
            extras_require={
                'pre-commit': [
                    'pre-commit~=2.15',
                    'pylint~=2.11.1',
                ],
                'tests': [
                    'pytest~=5.4',
                    'pytest-cov~=2.7',
                    'coverage<5.0',
                ],
            },
        )
