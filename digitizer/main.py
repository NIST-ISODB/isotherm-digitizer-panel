import panel as pn
import panel.widgets as pw
import bokeh.models.widgets as bw
from io import StringIO
import json

from . import ValidationError
from .config import QUANTITIES
from .adsorbates import Adsorbates
from .validate import prepare_isotherm_dict

pn.extension()

class IsothermSubmissionForm():
    
    def __init__(self):
        self.required_inputs = []

        # isotherm metadata
        self.inp_doi = pw.TextInput(name='Article DOI', placeholder="10.1021/jacs.9b01891")
        self.inp_temperature = pw.TextInput(name='Temperature', placeholder='303')
        self.inp_adsorbent = pw.AutocompleteInput(name='Adsorbent Material', options=QUANTITIES['adsorbents']['names'], placeholder='Zeolite 5A')
        self.inp_isotherm_type = pw.Select(name='Isotherm type', options=QUANTITIES['isotherm_type']['names'])
        self.inp_measurement_type = pw.Select(name='Measurement type', options=QUANTITIES['measurement_type']['names'])
        self.inp_pressure_scale = pw.Checkbox(name='Logarithmic pressure scale')
        self.inp_isotherm_data = pw.TextAreaInput(name='Isotherm Data', placeholder='#pressure,composition1,adsorption1,...,total_adsorption(opt)\n1,2,3,4')
    
        # units metadata
        self.inp_pressure_units = pw.Select(name='Pressure units', options=QUANTITIES['pressure_units']['names'])
        self.inp_adsorption_units = pw.AutocompleteInput(name='Adsorption Units', options=QUANTITIES['adsorption_units']['names'], placeholder='mmol/g')
        self.inp_composition_type = pw.Select(name='Composition type', options=QUANTITIES['composition_type']['names'])
        self.inp_concentration_units = pw.AutocompleteInput(name='Concentration Units', options=QUANTITIES['concentration_units']['names'], placeholder='mmol/g')
        
        # digitizer info
        self.inp_source_type = pw.TextInput(name='Source type', placeholder="Figure 1")
        self.inp_digitizer = pw.TextInput(name='Digitizer', placeholder="Your full name")
        
        # buttons
        self.btn_download = pn.widgets.FileDownload(filename='data.json', button_type='primary', callback=self.on_click_download)
        # btn_download.on_click(on_click_download)
        self.btn_prefill = pn.widgets.Button(name='Prefill', button_type='primary')
        self.btn_prefill.on_click(self.on_click_prefill)
        self.out_info = bw.PreText(text='Press download to download json')
        self.inp_adsorbates = Adsorbates(required_inputs=self.required_inputs)  # needs to add itself to required_inputs

        # Handle required inputs
        self.required_inputs += [self.inp_doi, self.inp_adsorbent, self.inp_temperature, self.inp_isotherm_data,
                    self.inp_pressure_units,
                    self.inp_adsorption_units, self.inp_composition_type, self.inp_source_type, self.inp_digitizer]
        for inp in self.required_inputs:
            inp.css_classes = ['required']
        
    def on_click_download(self):
        """Download JSON file."""
        self.out_info.text = ''
    
        try:
            data = prepare_isotherm_dict(self)
        except (ValidationError, ValueError) as  e:
            self.btn_download.button_type = 'warning'
            self.out_info.text = str(e)
            raise
    
        return StringIO(json.dumps(data, indent=4))

    def on_click_prefill(self, event):
        """Prefill form for testing purposes."""
        for inp in self.required_inputs:
            try:
                inp.value = inp.placeholder
            except AttributeError:
                # select fields have no placeholder (but are currently pre-filled)
                pass
    
    @property
    def layout(self):
        """Return form layout."""
        return pn.Column(
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
            pn.Row(self.btn_download, self.btn_prefill),
            self.out_info,
        )

form = IsothermSubmissionForm()
form.layout.servable()
