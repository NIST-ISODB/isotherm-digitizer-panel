# -*- coding: utf-8 -*-
"""Main layout of app.
"""
import os
import panel as pn
from .check import IsothermCheckView
from .forms import IsothermSingleComponentForm, IsothermMultiComponentForm
from . import TEMPLATES_DIR

# load CSS
with open(os.path.join(TEMPLATES_DIR, 'style.css')) as handle:
    css = handle.read()
pn.extension(raw_css=[css])

# prepare tabs
plot = IsothermCheckView()

tabs = pn.Tabs(css_classes=['main-tab'])
tabs.extend([('Single-component', IsothermSingleComponentForm(plot=plot, tabs=tabs).layout),
             ('Multi-component', IsothermMultiComponentForm(plot=plot, tabs=tabs).layout), ('Check', plot.layout)])

# create layout
template = pn.template.BootstrapTemplate(title='Isotherm Digitizer')
template.main.append(
    pn.pane.HTML('''
<p>Digitize isotherms to be added to the
<a target="_blank" href="https://adsorption.nist.gov/index.php#home">NIST/ARPA-E database of Novel and emerging adsorbent materials</a>.
</p>''',
                 width=940))
template.main.append(tabs)
template.servable(title='Isotherm Digitizer')
