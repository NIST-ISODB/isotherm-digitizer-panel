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

tabs.servable()
