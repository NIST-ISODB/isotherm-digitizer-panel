# -*- coding: utf-8 -*-
"""Isotherm plotting."""
from io import StringIO
from traitlets import HasTraits, observe, Instance
import panel as pn
import bokeh.models as bmd
from bokeh.plotting import figure

from .submission import Submissions, Isotherm
from .footer import footer

TOOLS = ['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save']


def get_bokeh_plot(isotherm_dict, pressure_scale='linear'):
    """Plot isotherm using bokeh.

    :returns: bokeh Figure instance
    """
    title = f'{isotherm_dict["articleSource"]}, {isotherm_dict["adsorbent"]["name"]}, {isotherm_dict["temperature"]} K'
    p = figure(tools=TOOLS, x_axis_type=pressure_scale, title=title)  # pylint: disable=invalid-name

    pressures = [point['pressure'] for point in isotherm_dict['isotherm_data']]

    for i in range(len(isotherm_dict['adsorbates'])):
        adsorbate = isotherm_dict['adsorbates'][i]
        adsorption = [point['species_data'][i]['adsorption'] for point in isotherm_dict['isotherm_data']]

        data = bmd.ColumnDataSource(data=dict(index=range(len(pressures)), pressure=pressures, adsorption=adsorption))

        p.line(  # pylint: disable=too-many-function-args
            'pressure',
            'adsorption',
            source=data,
            legend_label=adsorbate['name'])
        p.circle(  # pylint: disable=too-many-function-args
            'pressure',
            'adsorption',
            source=data,
            legend_label=adsorbate['name'])

    # update labels
    p.xaxis.axis_label = 'Pressure [{}]'.format(isotherm_dict['pressureUnits'])
    p.yaxis.axis_label = 'Adsorption [{}]'.format(isotherm_dict['adsorptionUnits'])

    tooltips = [(p.xaxis.axis_label, '@pressure'), (p.yaxis.axis_label, '@adsorption')]
    hover = bmd.HoverTool(tooltips=tooltips)
    p.tools.pop()
    p.tools.append(hover)

    return p


def _get_figure_pane(figure_image):
    """Get Figure pane for display."""
    if figure_image:
        return figure_image.pane
    return pn.pane.HTML('')


class IsothermCheckView(HasTraits):
    """Consistency checks for digitized isotherms.
    """
    isotherm = Instance(Isotherm)

    def __init__(self, isotherm=None, observed_forms=None):
        """Create check of isotherm data for consistency check.

        :param isotherm: Isotherm instance (optional).
        :param observed_forms: list of IsothermForm instances to observe
        """
        super().__init__()

        if isotherm:
            self.isotherm = isotherm
        else:
            self.row = pn.Row(figure(tools=TOOLS), _get_figure_pane(None))

        self.btn_download = pn.widgets.FileDownload(filename='data.json',
                                                    button_type='primary',
                                                    callback=self.on_click_download)
        self.btn_add = pn.widgets.Button(name='Add to submission', button_type='primary')
        self.btn_add.on_click(self.on_click_add)

        self.inp_pressure_scale = pn.widgets.RadioButtonGroup(name='Pressure scale', options=['linear', 'log'])
        self.inp_pressure_scale.param.watch(self.on_click_set_scale, 'value')

        # observe input forms
        def on_change_update(change):
            self.isotherm = change['new']

        if observed_forms:
            for form in observed_forms:
                form.observe(on_change_update, names=['isotherm'])

        # observe submission form and propagate changes to input forms
        self.observed_forms = observed_forms

        def on_load_update(change):
            self.isotherm = change['new']
            # todo: reload multi-component form depending on isotherm data  # pylint: disable=fixme
            for form in self.observed_forms[0:1]:
                form.isotherm = change['new']

        self.submissions = Submissions()
        self.submissions.observe(on_load_update, names=['loaded_isotherm'])

    @observe('isotherm')
    def _observe_isotherm(self, change):
        isotherm = change['new']
        self.row[0] = get_bokeh_plot(isotherm.json)
        self.row[1] = _get_figure_pane(isotherm.figure_image)

    def on_click_download(self):
        """Download JSON file."""
        return StringIO(self.isotherm.json_str)

    def on_click_add(self, event):  # pylint: disable=unused-argument
        """Add isotherm to submission."""
        self.submissions.append(self.isotherm)

    def on_click_set_scale(self, event):  # pylint: disable=unused-argument
        """Set pressure scale."""
        self.row[0] = get_bokeh_plot(self.isotherm.json, pressure_scale=self.inp_pressure_scale.value)

    @property
    def layout(self):
        """Return layout."""
        return pn.Column(self.row, self.inp_pressure_scale, pn.Row(self.btn_download, self.btn_add),
                         self.submissions.layout, footer)
