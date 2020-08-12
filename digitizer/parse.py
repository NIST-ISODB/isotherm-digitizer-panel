# -*- coding: utf-8 -*-
"""Prepare JSON output."""
from io import StringIO
import numpy as np
from .config import find_by_name, QUANTITIES
from . import ValidationError


def prepare_isotherm_dict(form):
    """Validate form contents and prepare JSON.

    :param form: Instance of IsothermForm
    :raises ValidationError: If validation fails.
    :returns: python dictionary with isotherm data
    """
    data = {}

    # Required fields provided?
    valid = True
    msg = ''

    for inp in form.required_inputs:
        if not inp.value or inp.value == 'Select':
            msg += 'Please provide ' + inp.name + '\n'
            valid = False
    if not valid:
        raise ValidationError(msg)

    # fill data
    data['DOI'] = form.inp_doi.value

    adsorbent_json = find_by_name(form.inp_adsorbent.value,
                                  QUANTITIES['adsorbents']['json'])
    data['adsorbent'] = {
        key: adsorbent_json[key]
        for key in ['name', 'hashkey']
    }
    try:
        data['temperature'] = int(form.inp_temperature.value)
    except Exception:
        raise ValidationError('Could not convert temperature to int.')

    adsorbates_json = [
        find_by_name(a.inp_name.value, QUANTITIES['adsorbates']['json'])
        for a in form.inp_adsorbates
    ]
    data['adsorbates'] = [{
        key: adsorbate[key]
        for key in ['name', 'InChIKey']
    } for adsorbate in adsorbates_json]
    data['isotherm_type'] = form.inp_isotherm_type.value
    data['measurement_type'] = form.inp_measurement_type.value

    measurements = np.genfromtxt(StringIO(form.inp_isotherm_data.value),
                                 delimiter=',',
                                 comments='#')
    measurements = np.array(measurements, ndmin=2)  # deal with single data row
    data['isotherm_data'] = [
        parse_pressure_row(pressure, data['adsorbates'], form)
        for pressure in measurements
    ]
    data['pressureUnits'] = form.inp_pressure_units.value
    if form.inp_saturation_pressure.value:
        data['saturationPressure'] = form.inp_saturation_pressure.value
    data['adsorptionUnits'] = form.inp_adsorption_units.value
    if form.__class__.__name__ == 'IsothermMultiComponentForm':
        data['compositionType'] = form.inp_composition_type.value
        data['concentrationUnits'] = form.inp_concentration_units.value
    data['articleSource'] = form.inp_source_type.value
    if 'table' in form.inp_source_type.value.lower():
        data['tabular'] = True
    data['digitizer'] = form.inp_digitizer.value

    return data


def parse_pressure_row(pressure, adsorbates, form):
    """Parse single pressure row.

    This can handle the following formats:
     * pressure,adsorption  (single-component form)
     * pressure,composition1,adsorption1,... (multi-component form)
     * pressure,composition1,adsorption1,...total_adsorption (multi-component form)
    """
    n_adsorbates = len(adsorbates)
    n_rows_no_total = 1 + 2 * n_adsorbates
    n_rows_total = n_rows_no_total + 1

    if form.__class__.__name__ == 'IsothermSingleComponentForm':
        if len(pressure) != 2:
            raise ValidationError('Expected 2 columns for pressure point "{}", found {}'. \
                                  format(str(pressure), len(pressure)), )
        measurement = {
            'pressure':
            pressure[0],
            'species_data': [{
                'InChIKey': adsorbates[0]['InChIKey'],
                'composition': '',
                'adsorption': pressure[1],
            }],
        }
    else:
        if len(pressure) == n_rows_no_total:
            has_total_pressure = False
        elif len(pressure) == n_rows_total:
            has_total_pressure = True
        else:
            raise ValidationError('Expected {} or {} columns for pressure point "{}", found {}'. \
                                  format(n_rows_no_total, n_rows_total, str(pressure), len(pressure)), )

        measurement = {
            'pressure':
            pressure[0],
            'species_data': [{
                'InChIKey': adsorbates[i]['InChIKey'],
                'composition': pressure[1 + 2 * i],
                'adsorption': pressure[2 + 2 * i],
            } for i in range(n_adsorbates)],
        }
        if has_total_pressure:
            measurement['total_pressure'] = pressure[-1]
        else:
            pass
            # TODO  # pylint: disable=fixme
    return measurement
