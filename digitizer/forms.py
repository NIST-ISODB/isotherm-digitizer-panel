# -*- coding: utf-8 -*-
"""Upload forms"""
import collections
import panel as pn
import panel.widgets as pw
import bokeh.models.widgets as bw

from . import ValidationError, config
from .config import QUANTITIES
from .adsorbates import Adsorbates
from .parse import prepare_isotherm_dict
from .read_json import read_isotherm_json

FigureImage = collections.namedtuple('FigureImage', ['data', 'filename'])


class IsothermSingleComponentForm():  # pylint:disable=too-many-instance-attributes
    """HTML form for uploading new isotherms."""
    def __init__(self, plot, tabs):  # pylint: disable=redefined-outer-name
        """Initialize form.

        :param plot: IsothermPlot instance for validation of results.
        :param tabs: Panel tabs instance for triggering tab switching.
        """
        self.plot = plot
        self.tabs = tabs

        # isotherm metadata
        self.inp_doi = pw.TextInput(name='Article DOI',
                                    placeholder='10.1021/jacs.9b01891')
        self.inp_doi.param.watch(self.on_change_doi, 'value')
        self.inp_temperature = pw.TextInput(name='Temperature',
                                            placeholder='303')
        self.inp_adsorbent = pw.AutocompleteInput(
            name='Adsorbent Material',
            options=QUANTITIES['adsorbents']['names'],
            placeholder='Zeolite 5A',
            case_sensitive=False)
        self.inp_isotherm_type = pw.Select(
            name='Isotherm type',
            options=['Select'] + QUANTITIES['isotherm_type']['names'])
        self.inp_measurement_type = pw.Select(
            name='Measurement type',
            options=['Select'] + QUANTITIES['measurement_type']['names'])
        self.inp_pressure_scale = pw.Checkbox(
            name='Logarithmic pressure scale')
        self.inp_isotherm_data = pw.TextAreaInput(
            name='Isotherm Data',
            height=200,
            placeholder=config.SINGLE_COMPONENT_EXAMPLE)
        self.inp_figure_image = pw.FileInput(name='Figure snapshot')

        # units metadata
        self.inp_pressure_units = pw.Select(
            name='Pressure units',
            options=['Select'] + QUANTITIES['pressure_units']['names'])
        self.inp_pressure_units.param.watch(self.on_change_pressure_units,
                                            'value')
        self.inp_saturation_pressure = pw.TextInput(
            name='Saturation pressure [bar]', disabled=True)
        self.inp_adsorption_units = pw.AutocompleteInput(
            name='Adsorption Units',
            options=QUANTITIES['adsorption_units']['names'],
            placeholder='mmol/g',
            case_sensitive=False)

        # digitizer info
        self.inp_source_type = pw.TextInput(name='Source type',
                                            placeholder='Figure 1')
        self.inp_tabular = pw.Checkbox(
            name='Tabular Data (i.e., not digitized from a graphical source)')
        self.inp_digitizer = pw.TextInput(name='Digitizer',
                                          placeholder='Your full name')

        # fill form from JSON upload
        self.inp_json = pw.FileInput(name='Upload JSON Isotherm')

        # buttons
        self.btn_prefill = pn.widgets.Button(name='Prefill',
                                             button_type='primary')
        self.btn_prefill.on_click(self.on_click_prefill)
        self.out_info = bw.PreText(
            text='Press "Plot" in order to download json.')
        self.inp_adsorbates = Adsorbates(show_controls=False, )
        self.btn_plot = pn.widgets.Button(name='Plot', button_type='primary')
        self.btn_plot.on_click(self.on_click_plot)

        self.btn_xferjson = pn.widgets.Button(name='Transfer data from JSON',
                                              button_type='primary')
        self.btn_xferjson.on_click(self.on_click_xferjson)

        for inp in self.required_inputs:
            inp.css_classes = ['required']

        # create layout
        self.layout = pn.Column(
            pn.pane.HTML('<h2>Isotherm Metadata</h2>'), self.inp_doi,
            self.inp_adsorbent, self.inp_temperature,
            self.inp_adsorbates.column, self.inp_isotherm_type,
            self.inp_measurement_type, self.inp_pressure_scale,
            pn.pane.HTML("""We recommend using the
                <b><a href='https://apps.automeris.io/wpd/' target="_blank">WebPlotDigitizer</a></b>"""
                         ), self.inp_isotherm_data,
            pn.Row(pn.pane.HTML("""Attach Isotherm Graphics"""),
                   self.inp_figure_image), pn.pane.HTML('<h2>Units</h2>'),
            pn.Row(self.inp_pressure_units,
                   self.inp_saturation_pressure), self.inp_adsorption_units,
            pn.pane.HTML('<h2>Digitization</h2>'), self.inp_source_type,
            self.inp_tabular, self.inp_digitizer,
            pn.Row(self.btn_plot, self.btn_prefill), self.out_info,
            pn.pane.HTML('<h2>Input Data from existing JSON Isotherm</h2>'),
            pn.Row(self.inp_jsondata, self.btn_xferjson))

    @property
    def required_inputs(self):
        """Required inputs."""
        return [
            self.inp_doi, self.inp_adsorbent, self.inp_temperature,
            self.inp_isotherm_data, self.inp_pressure_units,
            self.inp_adsorption_units, self.inp_source_type, self.inp_digitizer
        ] + self.inp_adsorbates.inputs

    def on_change_doi(self, event):
        """Warn, if DOI already known."""
        doi = event.new
        if doi in config.DOIs:
            self.log('DOI {} already present in database.'.format(doi),
                     level='warning')

    def on_change_pressure_units(self, event):
        """Toggle saturation pressure input depending on pressure units selection."""
        pressure_unit = event.new
        if pressure_unit == 'RELATIVE (specify units)':
            self.inp_saturation_pressure.disabled = False
        else:
            self.inp_saturation_pressure.disabled = True

    def on_click_prefill(self, event):  # pylint: disable=unused-argument
        """Prefill form for testing purposes."""
        for inp in self.required_inputs:
            try:
                inp.value = inp.placeholder
            except AttributeError:
                # select fields have no placeholder (but are currently pre-filled)
                pass

        self.inp_pressure_units.value = 'bar'
        self.inp_figure_image.value = config.FIGURE_EXAMPLE
        self.inp_figure_image.filename = config.FIGURE_FILENAME_EXAMPLE

    def on_click_plot(self, event):  # pylint: disable=unused-argument
        """Plot isotherm."""
        try:
            data = prepare_isotherm_dict(self)
        except (ValidationError, ValueError) as exc:
            self.log(str(exc), level='error')
            raise

        figure_image = FigureImage(data=self.inp_figure_image.value,
                                   filename=self.inp_figure_image.filename
                                   ) if self.inp_figure_image.value else None
        self.plot.update(data, figure_image=figure_image)
        self.tabs.active = 2

    def on_click_xferjson(self, event):  # pylint: disable=unused-argument, disable=too-many-branches
        """Call supporting function to import from input JSON"""
        read_isotherm_json(self)

    def log(self, msg, level='info'):
        """Print log message.

        Note: For some reason, simply updating the .text property of the PreText widget stopped working after moving
        to tabs (TODO: open issue on panel for this).
        """
        #self.layout.remove(self.out_info)
        self.layout.pop(-1)
        self.out_info.text = msg
        self.layout.append(self.out_info)

        if level == 'info':
            self.btn_plot.button_type = 'primary'
        elif level == 'warning':
            self.btn_plot.button_type = 'warning'
        elif level == 'error':
            self.btn_plot.button_type = 'danger'


class IsothermMultiComponentForm(IsothermSingleComponentForm):  # pylint:disable=too-many-instance-attributes
    """Initialize form.

    :param plot: IsothermPlot instance for validation of results.
    :param tabs: Panel tabs instance for triggering tab switching.
    """
    def __init__(self, plot, tabs):
        """Initialize form.

        :param plot: IsothermPlot instance for validation of results.
        :param tabs: Panel tabs instance for triggering tab switching.
        """

        self.inp_composition_type = pw.Select(
            name='Composition type',
            options=['Select'] + QUANTITIES['composition_type']['names'])
        self.inp_composition_type.param.watch(self.on_change_composition_type,
                                              'value')
        self.inp_concentration_units = pw.AutocompleteInput(
            name='Concentration Units',
            options=QUANTITIES['concentration_units']['names'],
            placeholder='mmol/g',
            case_sensitive=False,
            disabled=True)

        super().__init__(plot, tabs)

        self.inp_adsorbates = Adsorbates(show_controls=True, )

        self.inp_isotherm_data = pw.TextAreaInput(
            name='Isotherm Data',
            height=200,
            placeholder=config.MULTI_COMPONENT_EXAMPLE)

        # modified prefill function
        self.btn_prefill.on_click(self.on_click_prefill)

        self.layout = pn.Column(
            pn.pane.HTML('<h2>Isotherm Metadata</h2>'), self.inp_doi,
            self.inp_adsorbent, self.inp_temperature,
            self.inp_adsorbates.column, self.inp_isotherm_type,
            self.inp_measurement_type, self.inp_pressure_scale,
            pn.pane.HTML("""We recommend using the
                <b><a href='https://apps.automeris.io/wpd/' target="_blank">WebPlotDigitizer</a></b>"""
                         ), self.inp_isotherm_data,
            pn.Row(pn.pane.HTML("""Attach Isotherm Graphics"""),
                   self.inp_figure_image), pn.pane.HTML('<h2>Units</h2>'),
            pn.Row(self.inp_pressure_units,
                   self.inp_saturation_pressure), self.inp_adsorption_units,
            pn.Row(self.inp_composition_type, self.inp_concentration_units),
            pn.pane.HTML('<h2>Digitization</h2>'),
            self.inp_source_type, self.inp_digitizer,
            pn.Row(self.btn_plot, self.btn_prefill), self.out_info,
            pn.pane.HTML('<h2>Input Data from existing JSON Isotherm</h2>'),
            pn.Row(self.inp_jsondata, self.btn_xferjson))

    @property
    def required_inputs(self):
        """Required inputs."""
        return super().required_inputs + [self.inp_composition_type]

    def on_click_prefill(self, event):  # pylint: disable=unused-argument
        """Prefill form for testing purposes."""
        super().on_click_prefill(event)
        self.inp_composition_type.value = 'Mole Fraction'

    def on_change_composition_type(self, event):
        """Toggle concentration units input depending on pressure composition type."""
        composition_type = event.new
        if composition_type == 'Concentration (specify units)':
            self.inp_concentration_units.disabled = False
        else:
            self.inp_concentration_units.disabled = True
