# -*- coding: utf-8 -*-
"""Main layout of app.
"""
import os
import panel as pn
from .check import IsothermCheckView
from .forms import IsothermSingleComponentForm, IsothermMultiComponentForm
from .config import TEMPLATES_DIR

# load CSS
with open(os.path.join(TEMPLATES_DIR, 'style.css'), encoding='utf8') as handle:
    css = handle.read()
pn.extension(raw_css=[css])

# prepare tabs
tabs = pn.Tabs(css_classes=['main-tab'])
single = IsothermSingleComponentForm(tabs=tabs)
multi = IsothermMultiComponentForm(tabs=tabs)
check = IsothermCheckView(observed_forms=[single, multi])
tabs.extend([('Single-component', single.layout), ('Multi-component', multi.layout), ('Check', check.layout)])

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
