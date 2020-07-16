import panel as pn
import panel.widgets as pw

from .config import MATERIALS_LIST

pn.extension()

inp_doi = pw.TextInput(name='Article DOI', placeholder="10.1021/jacs.9b01891")
inp_temperature = pw.TextInput(name='Temperature')

class AdsorbentSingle():
    """Input form for describing one adsorbent."""
    def __init__(self):
        self.show_form = False

        self.inp_name = pw.AutocompleteInput(name='Adsorbent', options=MATERIALS_LIST)

        self.btn_add = pw.Button(name='+', button_type='primary')
        self.btn_add.on_click(self.on_click_toggle)

        self.inp_refcode = pw.TextInput(name='Refcode')
        self.column = pn.Column()
        self.update()
        
    def on_click_toggle(self, event):
        """Toggle visibility of form."""
        self.show_form = not self.show_form
        self.update()
        
    def update(self):
        #self.column.clear()
        if not self.show_form:
            self.column.append(pn.Row(self.inp_name, self.btn_add))
        else:
            self.column.append(
                pn.Row(self.inp_name, self.btn_add),
                self.inp_name,
                self.inp_refcode,
            )

    @property
    def adsorbent_dict(self):
        """Dictionary with adsorbent info"""
        pass



btn_submit = pn.widgets.Button(name='Submit', button_type='primary')

def on_click_submit(event):
    """Validate form contents."""
    data = {}
    
    try:
        data['temperature'] = int(inp_temperature)
    except Exception as e:
        inp_temperature.warning(str(e))
        btn_submit.button_type = 'warning'
        #import pdb; pdb.set_trace()
        inp_temperature.warning = str(e)
        inp_temperature.message = str(e)
        
btn_submit.on_click(on_click_submit)


column = pn.Column(
    pn.pane.HTML("""<h2>Add Paper</h2>"""),
    inp_doi,
    #pn.Row(inp_doi, btn_doi),
    inp_temperature,
    AdsorbentSingle().column,
    btn_submit,
    #inp_title,
    #inp_year,
    #inp_reference,
    #inp_paper_id,
    #btn_add_paper,
)
column.servable()

#gspec = pn.GridSpec(sizing_mode='stretch_both', max_width=1000, max_height=300)
#gspec[0, 0] = explorer.param
#gspec[:2, 1:4] = explorer.plot
#gspec[1, 0] = explorer.msg
#
#gspec.servable()
