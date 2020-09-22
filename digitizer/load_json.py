# -*- coding: utf-8 -*-
"""Functions to read from existing JSON files"""
import json

from .config import QUANTITIES, find_by_key
from .adsorbates import AdsorbateWithControls

CATEGORY_CONV = [('exp', 'Experiment'), ('sim', 'Simulation'), ('mod', 'Modeling'), ('ils', 'Interlaboratory Study'),
                 ('qua', 'Quantum/AB Initio/DFT')]


def lookup_species_name(species, species_type):
    """Look up adsorbent or adsorbate species from a hash or name"""
    if species_type == 'adsorbates':
        key_type = 'InChIKey'
    elif species_type == 'adsorbents':
        key_type = 'hashkey'
    else:
        raise AttributeError('Species type {} not understood'.format(species_type))
    if key_type in species.keys():
        # Look up by hash first
        output = find_by_key(species[key_type], key_type, QUANTITIES[species_type]['json'])
    elif 'name' in species.keys():
        # Fall back on name
        output = species
    else:
        raise ValueError('Adsorbate or Adsorbent metadata in JSON incomplete')
    return output['name']


def load_isotherm_json(form, json_string):  # pylint: disable=too-many-branches,too-many-statements
    """Populate form with data from JSON.

    :param json_string: JSON string
    :param form: IsothermForm instance to fill
    """
    input_data = json.loads(json_string)
    # Pre-process some fields
    try:
        input_data['isotherm_type'] = input_data['isotherm_type'].capitalize()
    except KeyError:
        pass

    for short, full in CATEGORY_CONV:
        try:
            if input_data['category'] == short:
                input_data['category'] = full
        except KeyError:
            pass

    # Generic Import Handler
    mappings = [
        (form.inp_doi, 'DOI'),
        (form.inp_temperature, 'temperature'),
        (form.inp_isotherm_type, 'isotherm_type'),
        (form.inp_measurement_type, 'category'),
        (form.inp_adsorption_units, 'adsorptionUnits'),
        (form.inp_source_type, 'articleSource'),
        (form.inp_digitizer, 'digitizer'),
    ]
    for (inp, key) in mappings:
        try:
            inp.value = str(input_data[key])
        except KeyError:
            pass

    # Special Import Handler for pressure units
    if input_data['pressureUnits'] == 'RELATIVE':
        form.inp_pressure_units.value = 'RELATIVE (specify units)'
        try:
            form.inp_saturation_pressure.value = str(input_data['saturationPressure'])
        except KeyError:
            pass
    else:
        try:
            form.inp_pressure_units.value = input_data['pressureUnits']
        except KeyError:
            pass

    # Special Import Handler for Booleans
    #   Allow true = 1
    for (inp, key) in [(form.inp_pressure_scale, 'log_scale'), (form.inp_tabular, 'tabular_data')]:
        try:
            if input_data[key] or input_data[key] == 1:
                inp.value = True
        except KeyError:
            pass

    # Look up adsorbent from input JSON
    form.inp_adsorbent.value = lookup_species_name(input_data['adsorbent'], 'adsorbents')

    if form.__class__.__name__ == 'IsothermMultiComponentForm':
        # Fields specific to Multicomponent Isotherms
        composition_conv = [('massratio', 'Mass Ratio'), ('moleratio', 'Mole Ratio'), ('massfraction', 'Mass Fraction'),
                            ('molefraction', 'Mole Fraction'), ('volumefraction', 'Volume Fraction'),
                            ('partialpressure', 'Partial Presure'), ('relhumidity', 'Relative Humidity'),
                            ('concentration', 'Concentration (specify units)')]
        for short, full in composition_conv:
            try:
                if input_data['compositionType'] == short:
                    input_data['compositionType'] = full
            except KeyError:
                pass
        try:
            form.inp_composition_type.value = input_data['compositionType']
        except KeyError:
            pass
        if form.inp_composition_type.value == 'Concentration (specify units)':
            form.inp_concentration_units.disabled = False
            try:
                form.inp_concentration_units.value = input_data['concentrationUnits']
            except KeyError:
                pass
        # Convert the JSON isotherm data to columns and fill in adsorbates
        form.inp_isotherm_data.value = read_multicomponent_columns(form, input_data)
    else:
        # Convert the JSON isotherm data to columns and fill in adsorbate
        form.inp_isotherm_data.value = read_singlecomponent_columns(form, input_data)


def read_singlecomponent_columns(form, input_data):
    """Convert the JSON-structured isotherm data to columns"""
    isotherm_block = input_data['isotherm_data']
    # Fill in adsorbate by InChIKey
    form.inp_adsorbates.data[0].inp_name.value = lookup_species_name(input_data['adsorbates'][0], 'adsorbates')
    # Extract data from each measurement
    lines = '#pressure,adsorption\n'
    for measurement in isotherm_block:
        line = str(measurement['pressure']) + ','
        line += str(measurement['species_data'][0]['adsorption'])
        lines += line + '\n'
    return lines


def read_multicomponent_columns(form, input_data):
    """Convert a multicomponent isotherm block to columns"""
    isotherm_block = input_data['isotherm_data']
    # Pull the adsorbates from the first measurement to create a list for cross-referencing
    try:
        adsorbates = sorted([x['InChIKey'] for x in isotherm_block[0]['species_data']])
    except KeyError:
        return ''
    # Add adsorbates to the form and fill in by InChIKey
    for (i, adsorbate) in enumerate(adsorbates):
        if i > 0:
            form.inp_adsorbates.append(AdsorbateWithControls(parent=form.inp_adsorbates))
        form.inp_adsorbates.data[i].inp_name.value = lookup_species_name({'InChIKey': adsorbate}, 'adsorbates')
    # Add any adsorbates not in the measurement data blocks
    for adsorbate in input_data['adsorbates']:
        if adsorbate['InChIKey'] not in adsorbates:
            form.inp_adsorbates.append(AdsorbateWithControls(parent=form.inp_adsorbates))
            form.inp_adsorbates.data[-1].inp_name.value = lookup_species_name(adsorbate, 'adsorbates')
    # Extract data from each measurement
    lines = '#pressure,composition1,adsorption1,...,total_adsorption(opt)\n'
    try:
        for measurement in isotherm_block:
            line = str(measurement['pressure']) + ','
            temp_list = sorted(measurement['species_data'], key=lambda k: k['InChIKey'])
            for species in temp_list:
                line += str(species['composition']) + ','
                line += str(species['adsorption']) + ','
            line = line.rstrip(',')
            if 'total_adsorption' in measurement:
                line += ',' + str(measurement['total_adsorption'])
            lines += line + '\n'
    except KeyError:
        pass

    return lines
