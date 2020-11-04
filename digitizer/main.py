# -*- coding: utf-8 -*-
"""Main layout of app.
"""
import panel as pn
from .plot import IsothermPlot
from .forms import IsothermSingleComponentForm, IsothermMultiComponentForm

pn.extension()

plot = IsothermPlot()

tabs = pn.Tabs(css_classes=['main-tab'])
tabs.extend([('Single-component', IsothermSingleComponentForm(plot=plot, tabs=tabs).layout),
             ('Multi-component', IsothermMultiComponentForm(plot=plot, tabs=tabs).layout), ('Plot', plot.layout)])

column = pn.Column()
column.append(pn.pane.HTML('<h2>Isotherm Digitizer</h2>'))
column.append(
    pn.pane.HTML('''
<div>Digitize isotherms to be added to the
<a target="_blank" href="https://adsorption.nist.gov/index.php#home">NIST/ARPA-E database of Novel and emerging adsorbent materials</a>.
</div>'''))
column.append(tabs)
column.servable(title='Isotherm Dig')
