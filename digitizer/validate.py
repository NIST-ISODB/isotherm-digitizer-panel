"""Prepare JSON output."""
from .config import find_by_name, QUANTITIES
from io import StringIO
import numpy as np
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
        if not inp.value:
            msg += 'Please provide ' + inp.name + '\n'
            valid = False
    if not valid:
        raise ValidationError(msg)

    # Fill data
    data['DOI'] = form.inp_doi.value
    data['adsorbent'] = find_by_name(form.inp_adsorbent.value, QUANTITIES['adsorbents']['json'])
    try:
        data['temperature'] = int(form.inp_temperature.value)
    except Exception as e:
        raise ValidationError('Could not convert temperature to int.')
    adsorbate_list = [ a.inp_name.value for a in form.inp_adsorbates ]
    n_adsorbates = len(adsorbate_list)
    data['adsorbates'] = [ find_by_name(name, QUANTITIES['adsorbates']['json']) for name in adsorbate_list]
    data['isotherm_type'] = form.inp_isotherm_type.value
    data['measurement_type'] = form.inp_measurement_type.value

    data['isotherm_data'] = []
    isotherm_pressures = np.genfromtxt(StringIO(form.inp_isotherm_data.value), delimiter=',', comments='#')
    isotherm_pressures = np.array(isotherm_pressures, ndmin=2)  # deal with case of single data row
    n_rows_no_total = 1 + 2*n_adsorbates
    n_rows_total = n_rows_no_total + 1
    for pressure in isotherm_pressures:
        if len(pressure) == n_rows_no_total:
            has_total_pressure = False
        elif len(pressure) == n_rows_total:
            has_total_pressure = True
        else:
            raise ValidationError('Expected {} or {} columns for pressure point "{}", found {}'. \
                             format(n_rows_no_total, n_rows_no_total, str(pressure), len(pressure)), )

        species_data = [{
                'InChIKey': data['adsorbates'][i]['InChIKey'],
                'composition': pressure[1+2*i],
                'adsorption': pressure[2 + 2 * i],
            } for i in range(n_adsorbates)]


        point = {
            'pressure': pressure[0],
            'species_data': species_data,
        }
        if has_total_pressure:
            point['total_pressure'] = pressure[-1]
        else:
            pass
            # TODO
        data['isotherm_data'].append(point)

    data['pressureUnits'] = form.inp_pressure_units.value
    data['adsorptionUnits'] = form.inp_adsorption_units.value
    data['compositionType'] = form.inp_composition_type.value
    data['concentrationUnits'] = ''
    data['articleSource'] = form.inp_source_type.value
    data['digitizer'] = form.inp_digitizer.value

    return data