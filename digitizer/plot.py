# -*- coding: utf-8 -*-
"""Isotherm plotting."""
from io import StringIO
import json
import panel as pn
import bokeh.models as bmd
from bokeh.plotting import figure

TOOLS = ['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save']


class IsothermPlot():
    """Plot of isotherm data for consistency check.
    """
    def __init__(self, isotherm_dict=None):
        """Create plot of isotherm data for consistency check.

        :param isotherm_dict: Dictionary with isotherm data (optional).
        """
        self.figure = figure(tools=TOOLS)
        self.isotherm_dict = isotherm_dict
        self.btn_download = pn.widgets.FileDownload(
            filename='data.json',
            button_type='primary',
            callback=self.on_click_download)
        # btn_download.on_click(on_click_download)

    def update(self, isotherm_dict):
        """Update isotherm plot with provided data."""
        self.isotherm_dict = isotherm_dict
        self.figure = self.get_bokeh_plot(isotherm_dict)

    def get_bokeh_plot(self, isotherm_dict):
        """Plot isotherm using bokeh.

        :returns: bokeh Figure instance
        """

        p = self.figure  # pylint: disable=invalid-name
        #p = figure(tools=TOOLS, height=350, width=550)
        # p.xgrid.grid_line_color = None

        # # Colored background
        # colors = ['red', 'orange', 'green', 'yellow', 'cyan', 'pink', 'palegreen']
        # start = 0
        # for i, steps in enumerate(out_dict['stage_info']['nsteps']):
        #     end = start + steps
        #     p.add_layout(bmd.BoxAnnotation(left=start, right=end, fill_alpha=0.2, fill_color=colors[i]))
        #     start = end
        #
        # # Trace line and markers
        # p.line('index', 'energy', source=data, line_color='blue')
        # p.circle('index', 'energy', source=data, line_color='blue', size=3)

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
        return StringIO(json.dumps(self.isotherm_dict, indent=4))

    @property
    def layout(self):
        """Return layout."""
        return pn.Column(
            pn.pane.HTML("""<h2>Isotherm plot</h2>"""),
            pn.pane.Bokeh(self.figure),
            self.btn_download,
        )
