# -*- coding: utf-8 -*-
"""Main layout of app.

Includes layout of upload form.
"""
import panel as pn
import panel.widgets as pw
import bokeh.models.widgets as bw

from . import ValidationError
from .config import QUANTITIES, SINGLE_COMPONENT_EXAMPLE, MULTI_COMPONENT_EXAMPLE
from .adsorbates import Adsorbates
from .parse import prepare_isotherm_dict
from .plot import IsothermPlot

pn.extension()


class IsothermSubmissionForm():  # pylint:disable=too-many-instance-attributes
    """HTML form for uploading new isotherms."""
    def __init__(self, plot, mode='multi-component'):  # pylint: disable=redefined-outer-name
        """

        :param plot: IsothermPlot instance for validation of results.
        :param mode: Either 'multi-component' or 'single-component'
        """
        self.plot = plot
        self.mode = mode
        self.required_inputs = []

        # isotherm metadata
        self.inp_doi = pw.TextInput(name='Article DOI',
                                    placeholder='10.1021/jacs.9b01891')
        self.inp_temperature = pw.TextInput(name='Temperature',
                                            placeholder='303')
        self.inp_adsorbent = pw.AutocompleteInput(
            name='Adsorbent Material',
            options=QUANTITIES['adsorbents']['names'],
            placeholder='Zeolite 5A')
        self.inp_isotherm_type = pw.Select(
            name='Isotherm type', options=QUANTITIES['isotherm_type']['names'])
        self.inp_measurement_type = pw.Select(
            name='Measurement type',
            options=QUANTITIES['measurement_type']['names'])
        self.inp_pressure_scale = pw.Checkbox(
            name='Logarithmic pressure scale')
        self.inp_isotherm_data = pw.TextAreaInput(
            name='Isotherm Data',
            height=200,
            placeholder=MULTI_COMPONENT_EXAMPLE
            if self.mode == 'multi-component' else SINGLE_COMPONENT_EXAMPLE)

        # units metadata
        self.inp_pressure_units = pw.Select(
            name='Pressure units',
            options=QUANTITIES['pressure_units']['names'])
        self.inp_adsorption_units = pw.AutocompleteInput(
            name='Adsorption Units',
            options=QUANTITIES['adsorption_units']['names'],
            placeholder='mmol/g')
        self.inp_composition_type = pw.Select(
            name='Composition type',
            options=QUANTITIES['composition_type']['names'])
        self.inp_concentration_units = pw.AutocompleteInput(
            name='Concentration Units',
            options=QUANTITIES['concentration_units']['names'],
            placeholder='mmol/g')

        # digitizer info
        self.inp_source_type = pw.TextInput(name='Source type',
                                            placeholder='Figure 1')
        self.inp_digitizer = pw.TextInput(name='Digitizer',
                                          placeholder='Your full name')

        # buttons
        self.btn_prefill = pn.widgets.Button(name='Prefill',
                                             button_type='primary')
        self.btn_prefill.on_click(self.on_click_prefill)
        self.out_info = bw.PreText(
            text='Press "Plot" in order to download json.')
        self.inp_adsorbates = Adsorbates(
            required_inputs=self.required_inputs,
            show_controls=mode == 'multi-component',
        )  # needs to add itself to required_inputs
        self.btn_plot = pn.widgets.Button(name='Plot', button_type='primary')
        self.btn_plot.on_click(self.on_click_plot)

        # Handle required inputs
        self.required_inputs += [
            self.inp_doi, self.inp_adsorbent, self.inp_temperature,
            self.inp_isotherm_data, self.inp_pressure_units,
            self.inp_adsorption_units, self.inp_composition_type,
            self.inp_source_type, self.inp_digitizer
        ]
        for inp in self.required_inputs:
            inp.css_classes = ['required']

        # create layout
        self.layout = pn.Column(
            pn.pane.HTML("""<h2>Isotherm Metadata</h2>"""),
            self.inp_doi,
            self.inp_adsorbent,
            self.inp_temperature,
            self.inp_adsorbates.column,
            self.inp_isotherm_type,
            self.inp_measurement_type,
            self.inp_pressure_scale,
            self.inp_isotherm_data,
            pn.pane.HTML("""<h2>Units</h2>"""),
            self.inp_pressure_units,
            self.inp_adsorption_units,
            self.inp_composition_type,
            self.inp_concentration_units,
            pn.pane.HTML("""<h2>Digitization</h2>"""),
            self.inp_source_type,
            self.inp_digitizer,
            pn.Row(self.btn_plot, self.btn_prefill),
            self.out_info,
        )

    def on_click_prefill(self, event):  # pylint: disable=unused-argument
        """Prefill form for testing purposes."""
        for inp in self.required_inputs:
            try:
                inp.value = inp.placeholder
            except AttributeError:
                # select fields have no placeholder (but are currently pre-filled)
                pass

        self.inp_pressure_units.value = 'bar'
        self.inp_composition_type.value = 'Mass Ratio'

    def on_click_plot(self, event):  # pylint: disable=unused-argument
        """Plot isotherm."""
        try:
            data = prepare_isotherm_dict(self)
        except (ValidationError, ValueError) as exc:
            self.btn_plot.button_type = 'warning'
            self.log(str(exc))
            raise

        self.plot.update(data)
        tabs.active = 2

    def log(self, msg):
        """Print log message.

        Note: For some reason, simply updating the .text property of the PreText widget stopped working after moving
        to tabs (TODO: open issue on panel for this).
        """
        #self.layout.remove(self.out_info)
        self.layout.pop(-1)
        self.out_info.text = msg
        self.layout.append(self.out_info)


plot = IsothermPlot()

tabs = pn.Tabs(
    ('Single-component',
     IsothermSubmissionForm(plot=plot, mode='single-component').layout),
    ('Multi-component', IsothermSubmissionForm(plot=plot).layout),
    ('Plot', plot.layout),
)

tabs.servable()
