# -*- coding: utf-8 -*-
"""Isotherm plotting."""
from io import StringIO
import panel as pn
import bokeh.models as bmd
from bokeh.plotting import figure
from .submission import Submissions, Isotherm

TOOLS = ['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save']


def get_bokeh_plot(isotherm_dict, pressure_scale='linear'):
    """Plot isotherm using bokeh.

    :returns: bokeh Figure instance
    """
    p = figure(tools=TOOLS, x_axis_type=pressure_scale)  # pylint: disable=invalid-name

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


class IsothermPlot():
    """Plot of isotherm data for consistency check.
    """
    def __init__(self, isotherm_dict=None, figure_image=None):
        """Create plot of isotherm data for consistency check.

        :param isotherm_dict: Isotherm dictionary (optional).
        """
        self.row = pn.Row(figure(tools=TOOLS))
        self._isotherm_dict = isotherm_dict
        self._figure_image = figure_image

        self.btn_download = pn.widgets.FileDownload(filename='data.json',
                                                    button_type='primary',
                                                    callback=self.on_click_download)
        self.btn_download.data = ''  # bug in panel https://github.com/holoviz/panel/issues/1598
        self.btn_add = pn.widgets.Button(name='Add to submission', button_type='primary')
        self.btn_add.on_click(self.on_click_add)

        self.inp_pressure_scale = pn.widgets.RadioButtonGroup(name='Pressure scale', options=['linear', 'log'])
        self.inp_pressure_scale.param.watch(self.on_click_set_scale, 'value')

        self.submissions = Submissions()

    def update(self, isotherm_dict, figure_image=None):
        """Update isotherm plot with provided data.

        Updates figure as well as internal data representation.

        :param isotherm_dict: Dictionary with parsed isotherm data.
        :param figure_image: Byte stream with figure snapshot
        """
        self._isotherm_dict = isotherm_dict
        self._figure_image = figure_image
        self.row[0] = get_bokeh_plot(isotherm_dict)

    @property
    def isotherm(self):
        """Return Isotherm() instance."""
        isotherm_dict = self._isotherm_dict
        display_name = '{} ({})'.format(isotherm_dict['articleSource'], isotherm_dict['DOI'])
        return Isotherm(name=display_name, json=isotherm_dict, figure_image=self._figure_image)

    def on_click_download(self):
        """Download JSON file."""
        return StringIO(self.isotherm.json_str)

    def on_click_add(self, event):  # pylint: disable=unused-argument
        """Add isotherm to submission."""
        self.submissions.append(self.isotherm)

    def on_click_set_scale(self, event):  # pylint: disable=unused-argument
        """Set pressure scale."""
        self.row[0] = get_bokeh_plot(self._isotherm_dict, pressure_scale=self.inp_pressure_scale.value)

    @property
    def layout(self):
        """Return layout."""
        return pn.Column(
            pn.pane.HTML("""<h2>Isotherm plot</h2>"""),
            self.row,
            self.inp_pressure_scale,
            pn.Row(self.btn_download, self.btn_add),
            self.submissions.layout,
        )
