# -*- coding: utf-8 -*-
"""Prepare JSON output."""
from io import StringIO
import re
import datetime
import pandas as pd
import panel as pn

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

    try:
        adsorbent_json = find_by_name(form.inp_adsorbent.value, QUANTITIES['adsorbents']['json'])
    except ValueError:
        adsorbent_json = dict(name=form.inp_adsorbent.value, hashkey=None)

    data['adsorbent'] = {key: adsorbent_json[key] for key in ['name', 'hashkey']}
    try:
        data['temperature'] = int(form.inp_temperature.value)
    except ValueError as error_handler:
        raise ValidationError('Could not convert temperature to int.') from error_handler

    adsorbates_json = [find_by_name(a.inp_name.value, QUANTITIES['adsorbates']['json']) for a in form.inp_adsorbates]
    data['adsorbates'] = [{key: adsorbate[key] for key in ['name', 'InChIKey']} for adsorbate in adsorbates_json]
    data['isotherm_type'] = form.inp_isotherm_type.value
    data['category'] = form.inp_measurement_type.value
    form_type = 'single-component' if form.__class__.__name__ == 'IsothermSingleComponentForm' else 'multi-component'
    data['isotherm_data'] = parse_isotherm_data(form.inp_isotherm_data.value, data['adsorbates'], form_type=form_type)

    data['pressureUnits'] = form.inp_pressure_units.value
    if form.inp_saturation_pressure.value:
        try:
            data['saturationPressure'] = float(form.inp_saturation_pressure.value)
        except ValueError as error_handler:
            raise ValidationError('Could not convert saturationPressure to float.') from error_handler
    data['adsorptionUnits'] = form.inp_adsorption_units.value
    if form.__class__.__name__ == 'IsothermMultiComponentForm':
        data['compositionType'] = form.inp_composition_type.value
        data['concentrationUnits'] = form.inp_concentration_units.value
    else:
        data['compositionType'] = 'molefraction'  # default for single-component isotherm
        data['concentrationUnits'] = None
    data['articleSource'] = form.inp_source_type.value
    data['custom'] = form.inp_comment.value
    if form.inp_tabular.value:
        data['tabular_data'] = True
    data['digitizer'] = form.inp_digitizer.value
    data['associated_content'] = [form.inp_figure_image.filename]
    # 'associated_content' is a list in anticipation of multiple file selection
    # code for getting filenames will change

    # Log entry date
    data['date'] = datetime.date.today().strftime('%Y-%m-%d')
    # strftime is not strictly necessary but ensures correct YYYY-MM-DD format

    # Sanitize keys from optional menus
    for key in data:
        if data[key] == 'Select':
            data[key] = None

    return data


def parse_isotherm_data(measurements, adorbates, form_type='single-component'):
    """Parse text from isotherm data field.

    :param measurements: Data from text field
    :param adsorbates: Adsorbates dictionary
    :param form_type: 'single-component' or 'multi-component'
    :returns: python dictionary with isotherm data

    """
    for delimiter in ['\t', ';', '|', ',']:
        measurements = measurements.replace(delimiter, ' ')  # convert all delimiters to spaces
    measurements = re.sub(' +', ' ', measurements)  # collapse whitespace
    measurements = pd.read_table(
        StringIO(measurements),
        sep=',| ',
        #sep=' ',
        # for some reason, leaving only the space delimiter is causing a problem
        #  when lines have trailing whitespace. Need to check pandas documentation
        comment='#',
        header=None,
        engine='python')
    measurements = measurements.to_numpy(dtype=float)
    return [parse_pressure_row(pressure, adorbates, form_type) for pressure in measurements]


def parse_pressure_row(pressure, adsorbates, form_type):
    """Parse single pressure row.

    This can handle the following formats:
     * pressure,adsorption  (single-component form)
     * pressure,composition1,adsorption1,... (multi-component form)
     * pressure,composition1,adsorption1,...total_adsorption (multi-component form)
    """
    n_adsorbates = len(adsorbates)
    n_rows_no_total = 1 + 2 * n_adsorbates
    n_rows_total = n_rows_no_total + 1

    if form_type == 'single-component':
        if len(pressure) != 2:
            raise ValidationError('Expected 2 columns for pressure point "{}", found {}'. \
                                  format(str(pressure), len(pressure)), )
        measurement = {
            'pressure': pressure[0],
            'species_data': [{
                'InChIKey': adsorbates[0]['InChIKey'],
                'composition': '1.0',
                'adsorption': pressure[1],
            }],
            'total_adsorption': pressure[1]
        }
    else:
        if len(pressure) == n_rows_no_total:
            has_total_adsorption = False
        elif len(pressure) == n_rows_total:
            has_total_adsorption = True
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
        if has_total_adsorption:
            measurement['total_adsorption'] = pressure[-1]
        else:
            pass
            # TODO  # pylint: disable=fixme
    return measurement


class FigureImage:  # pylint: disable=too-few-public-methods
    """Representation of digitized image."""
    def __init__(self, data=None, filename=None):
        self.data = data
        self.filename = filename

    def _repr_png_(self):
        """Return png representation.

        Needed for display in "check" tab.
        """
        if self.data:
            return self.data
        return ''

    @property
    def pane(self):
        """Return PNG pane."""
        return pn.pane.PNG(object=self, width=400)
