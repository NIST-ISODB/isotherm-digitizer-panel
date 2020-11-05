# -*- coding: utf-8 -*-
"""Upload forms"""
import panel as pn
import panel.widgets as pw
import bokeh.models.widgets as bw
from traitlets import HasTraits, Instance

from . import ValidationError, config, restrict_kwargs
from .config import QUANTITIES, BIBLIO_API_URL
from .adsorbates import Adsorbates
from .parse import prepare_isotherm_dict, FigureImage
from .load_json import load_isotherm_json, load_isotherm_dict
from .footer import footer
from .submission import Isotherm


class IsothermSingleComponentForm(HasTraits):  # pylint:disable=too-many-instance-attributes
    """HTML form for uploading new isotherms."""

    isotherm = Instance(Isotherm)  # this traitlet is observed by the "check" view

    def __init__(self, tabs):  # pylint: disable=redefined-outer-name
        """Initialize form.

        :param tabs: Panel tabs instance for triggering tab switching.
        """
        super().__init__()
        self.tabs = tabs

        # isotherm metadata
        self.inp_doi = pw.TextInput(name='Article DOI', placeholder='10.1021/jacs.9b01891')
        self.inp_doi.param.watch(self.on_change_doi, 'value')
        self.inp_temperature = pw.TextInput(name='Temperature [K]', placeholder='303')
        self.inp_adsorbent = pw.AutocompleteInput(name='Adsorbent Material',
                                                  options=QUANTITIES['adsorbents']['names'],
                                                  placeholder='Zeolite 5A',
                                                  case_sensitive=False,
                                                  **restrict_kwargs)
        self.inp_isotherm_type = pw.Select(name='Isotherm type',
                                           options=['Select'] + QUANTITIES['isotherm_type']['names'])
        self.inp_measurement_type = pw.Select(name='Measurement type',
                                              options=['Select'] + QUANTITIES['measurement_type']['names'])
        self.inp_pressure_scale = pw.Checkbox(name='Logarithmic pressure scale')
        self.inp_isotherm_data = pw.TextAreaInput(name='Isotherm Data',
                                                  height=200,
                                                  placeholder=config.SINGLE_COMPONENT_EXAMPLE)
        self.inp_figure_image = pw.FileInput(name='Figure snapshot')

        # units metadata
        self.inp_pressure_units = pw.Select(name='Pressure units',
                                            options=['Select'] + QUANTITIES['pressure_units']['names'])
        self.inp_pressure_units.param.watch(self.on_change_pressure_units, 'value')
        self.inp_saturation_pressure = pw.TextInput(name='Saturation pressure [bar]', disabled=True)
        self.inp_adsorption_units = pw.AutocompleteInput(name='Adsorption Units',
                                                         options=QUANTITIES['adsorption_units']['names'],
                                                         placeholder='mmol/g',
                                                         case_sensitive=False,
                                                         **restrict_kwargs)

        # digitizer info
        self.inp_source_type = pw.TextInput(name='Source description', placeholder='Figure 1a')
        self.inp_tabular = pw.Checkbox(name='Tabular Data (i.e., not digitized from a graphical source)')
        self.inp_digitizer = pw.TextInput(name='Digitized by', placeholder='Your full name')

        # fill form from JSON upload
        self.inp_json = pw.FileInput(name='Upload JSON Isotherm')
        self.inp_json.param.watch(self.populate_from_json, 'value')

        # buttons
        self.btn_prefill = pn.widgets.Button(name='Prefill (default or from JSON)', button_type='primary')
        self.btn_prefill.on_click(self.on_click_populate)
        self.out_info = bw.PreText(text='Click "Check" in order to download json.')
        #self.out_info = pn.pane.Markdown(text='Click "Check" in order to download json.')
        self.inp_adsorbates = Adsorbates(show_controls=False)
        self.btn_plot = pn.widgets.Button(name='Check', button_type='primary')
        self.btn_plot.on_click(self.on_click_check)

        for inp in self.required_inputs:
            inp.css_classes = ['required']

        # create layout
        self.layout = pn.Column(
            self.inp_digitizer,
            self.inp_doi,
            pn.pane.HTML('<hr>'),
            self.inp_source_type,
            pn.Row(pn.pane.HTML("""Attach Figure Graphics"""), self.inp_figure_image),
            self.inp_measurement_type,
            self.inp_adsorbent,
            self.inp_adsorbates.column,
            self.inp_temperature,
            self.inp_isotherm_type,
            pn.Row(self.inp_pressure_units, self.inp_saturation_pressure),
            self.inp_pressure_scale,
            self.inp_adsorption_units,
            pn.pane.HTML("""We recommend the
                <b><a href='https://apps.automeris.io/wpd/' target="_blank">WebPlotDigitizer</a></b>
                for data extraction."""),
            self.inp_isotherm_data,
            self.inp_tabular,
            pn.Row(self.btn_plot, self.btn_prefill, self.inp_json),
            self.out_info,
            footer,
        )

    def populate_from_isotherm(self, isotherm):
        """Populate form from isotherm instance.

        :param isotherm:  Isotherm instance
        """
        load_isotherm_dict(form=self, isotherm_dict=isotherm.json)

        figure_image = isotherm.figure_image
        self.inp_figure_image.value = figure_image.data
        self.inp_figure_image.filename = figure_image.filename

    def populate_from_json(self, event):
        """Prefills form from JSON.

        This function observes the inp_json field.
        """
        load_isotherm_json(form=self, json_string=event.new)

    @property
    def required_inputs(self):
        """Required inputs."""
        return [
            self.inp_doi, self.inp_adsorbent, self.inp_temperature, self.inp_isotherm_data, self.inp_pressure_units,
            self.inp_adsorption_units, self.inp_source_type, self.inp_digitizer
        ] + self.inp_adsorbates.inputs

    def on_change_doi(self, event):
        """Warn, if DOI already known."""
        doi = event.new
        if doi in config.DOIs:
            self.log(f'{doi} already present in database (see {BIBLIO_API_URL}/{doi}.json ).', level='warning')

    def on_change_pressure_units(self, event):
        """Toggle saturation pressure input depending on pressure units selection."""
        pressure_unit = event.new
        if pressure_unit == 'RELATIVE (specify units)':
            self.inp_saturation_pressure.disabled = False
        else:
            self.inp_saturation_pressure.disabled = True

    def on_click_populate(self, event):  # pylint: disable=unused-argument
        """Populate form, either from JSON or with default values."""
        if self.inp_json.value:
            json_string = self.inp_json.value
            load_isotherm_json(form=self, json_string=json_string)
            self.inp_figure_image.value = None
            self.inp_figure_image.filename = None
        else:
            # Note: this could be replaced by loading a sample isotherm JSON (but makes it harder to edit defaults)
            # with open(DEFAULT_ISOTHERM_FILE) as handle:
            #     json_string = handle.read()
            # load_isotherm_json(form=self, json_string=json_string)

            for inp in self.required_inputs:
                try:
                    inp.value = inp.placeholder
                except AttributeError:
                    # select fields have no placeholder (but are currently pre-filled)
                    pass

            self.inp_pressure_units.value = 'bar'
            self.inp_figure_image.value = config.FIGURE_EXAMPLE
            self.inp_figure_image.filename = config.FIGURE_FILENAME_EXAMPLE

    def on_click_check(self, event):  # pylint: disable=unused-argument
        """Check isotherm."""
        try:
            data = prepare_isotherm_dict(self)
        except (ValidationError, ValueError) as exc:
            self.log(str(exc), level='error')
            raise

        figure_image = FigureImage(data=self.inp_figure_image.value,
                                   filename=self.inp_figure_image.filename) if self.inp_figure_image.value else None

        self.btn_plot.button_type = 'primary'
        self.log('')

        self.isotherm = Isotherm(data, figure_image)
        self.tabs.active = 2

    def log(self, msg, level='info'):
        """Print log message.

        Note: For some reason, simply updating the .text property of the PreText widget stopped working after moving
        to tabs (TODO: open issue on panel for this).
        """
        #self.layout.remove(self.out_info)
        self.layout.pop(-2)  # -1 is footer for the moment
        self.out_info.text = msg
        self.layout.insert(-1, self.out_info)  # inserts *before* -1

        if level == 'info':
            self.btn_plot.button_type = 'primary'
        elif level == 'warning':
            self.btn_plot.button_type = 'warning'
        elif level == 'error':
            self.btn_plot.button_type = 'danger'


class IsothermMultiComponentForm(IsothermSingleComponentForm):  # pylint:disable=too-many-instance-attributes
    """Initialize form.

    :param tabs: Panel tabs instance for triggering tab switching.
    """
    def __init__(self, tabs):
        """Initialize form.

        :param tabs: Panel tabs instance for triggering tab switching.
        """

        # new fields
        self.inp_composition_type = pw.Select(name='Composition type',
                                              options=['Select'] + QUANTITIES['composition_type']['names'])
        self.inp_composition_type.param.watch(self.on_change_composition_type, 'value')
        self.inp_concentration_units = pw.AutocompleteInput(name='Concentration Units',
                                                            options=QUANTITIES['concentration_units']['names'],
                                                            placeholder='Molarity (mol/l)',
                                                            case_sensitive=False,
                                                            disabled=True,
                                                            **restrict_kwargs)

        super().__init__(tabs)

        # override fields
        self.inp_adsorbates = Adsorbates(show_controls=True, )
        self.inp_isotherm_data = pw.TextAreaInput(name='Isotherm Data',
                                                  height=200,
                                                  placeholder=config.MULTI_COMPONENT_EXAMPLE)

        # modified prefill function
        self.btn_prefill.on_click(self.on_click_populate)

        # create layout
        self.layout = pn.Column(
            pn.pane.HTML('<div><b>Warning:</b> The multi-component form is not well tested</div>.'),
            self.inp_digitizer,
            self.inp_doi,
            pn.pane.HTML('<hr>'),
            self.inp_source_type,
            pn.Row(pn.pane.HTML("""Attach Figure Graphics"""), self.inp_figure_image),
            self.inp_measurement_type,
            self.inp_adsorbent,
            self.inp_adsorbates.column,
            self.inp_temperature,
            self.inp_isotherm_type,
            pn.Row(self.inp_pressure_units, self.inp_saturation_pressure),
            self.inp_pressure_scale,
            self.inp_adsorption_units,
            pn.Row(self.inp_composition_type, self.inp_concentration_units),
            pn.pane.HTML("""We recommend the
                <b><a href='https://apps.automeris.io/wpd/' target="_blank">WebPlotDigitizer</a></b>
                for data extraction."""),
            self.inp_isotherm_data,
            self.inp_tabular,
            pn.Row(self.btn_plot, self.btn_prefill, self.inp_json),
            self.out_info,
            footer,
        )

    @property
    def required_inputs(self):
        """Required inputs."""
        return super().required_inputs + [self.inp_composition_type]

    def on_click_populate(self, event):  # pylint: disable=unused-argument
        """Prefill form for testing purposes."""
        super().on_click_populate(event)
        self.inp_composition_type.value = 'Mole Fraction'

    def on_change_composition_type(self, event):
        """Toggle concentration units input depending on pressure composition type."""
        composition_type = event.new
        if composition_type == 'Concentration (specify units)':
            self.inp_concentration_units.disabled = False
        else:
            self.inp_concentration_units.disabled = True
