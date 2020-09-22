# -*- coding: utf-8 -*-
"""Isotherm plotting."""
from io import StringIO
import panel as pn
import bokeh.models as bmd
from bokeh.plotting import figure
from .submission import Submissions, Isotherm

TOOLS = ['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save']


class IsothermPlot():
    """Plot of isotherm data for consistency check.
    """
    def __init__(self, isotherm=None):
        """Create plot of isotherm data for consistency check.

        :param isotherm: Isotherm instance (optional).
        """
        self.figure = figure(tools=TOOLS)
        self.isotherm = isotherm
        self.btn_download = pn.widgets.FileDownload(
            filename='data.json',
            button_type='primary',
            callback=self.on_click_download)
        self.btn_download.data = ''  # bug in panel https://github.com/holoviz/panel/issues/1598
        self.btn_add = pn.widgets.Button(name='Add to submission',
                                         button_type='primary')
        self.btn_add.on_click(self.on_click_add)

        self.submissions = Submissions()

    def update(self, isotherm_dict, figure_image=None):
        """Update isotherm plot with provided data.

        :param isotherm_dict: Dictionary with parsed isotherm data.
        :param figure_image: Byte stream with figure snapshot
        """
        display_name = '{} ({})'.format(isotherm_dict['articleSource'],
                                        isotherm_dict['DOI'])
        self.isotherm = Isotherm(name=display_name,
                                 json=isotherm_dict,
                                 figure_image=figure_image)
        self.figure = self.get_bokeh_plot(isotherm_dict)

    def get_bokeh_plot(self, isotherm_dict):
        """Plot isotherm using bokeh.

        :returns: bokeh Figure instance
        """
        p = self.figure  # pylint: disable=invalid-name
        p.renderers = []  # reset plot

        pressures = [
            point['pressure'] for point in isotherm_dict['isotherm_data']
        ]

        for i in range(len(isotherm_dict['adsorbates'])):
            adsorbate = isotherm_dict['adsorbates'][i]
            adsorption = [
                point['species_data'][i]['adsorption']
                for point in isotherm_dict['isotherm_data']
            ]

            data = bmd.ColumnDataSource(data=dict(index=range(len(pressures)),
                                                  pressure=pressures,
                                                  adsorption=adsorption))

            p.line('pressure',
                   'adsorption',
                   source=data,
                   legend_label=adsorbate['name'])
            p.circle('pressure',
                     'adsorption',
                     source=data,
                     legend_label=adsorbate['name'])

        # update labels
        p.xaxis.axis_label = 'Pressure [{}]'.format(
            isotherm_dict['pressureUnits'])
        p.yaxis.axis_label = 'Adsorption [{}]'.format(
            isotherm_dict['adsorptionUnits'])

        tooltips = [(p.xaxis.axis_label, '@pressure'),
                    (p.yaxis.axis_label, '@adsorption')]
        hover = bmd.HoverTool(tooltips=tooltips)
        p.tools.pop()
        p.tools.append(hover)

        return p

    def on_click_download(self):
        """Download JSON file."""
        return StringIO(self.isotherm.json_str)

    def on_click_add(self, event):  # pylint: disable=unused-argument
        """Add isotherm to submission."""
        self.submissions.append(self.isotherm)

    @property
    def layout(self):
        """Return layout."""
        return pn.Column(
            pn.pane.HTML("""<h2>Isotherm plot</h2>"""),
            pn.pane.Bokeh(self.figure),
            pn.Row(self.btn_download, self.btn_add),
            self.submissions.layout,
        )
