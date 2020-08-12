# -*- coding: utf-8 -*-
"""Store stack of submissions"""
from io import BytesIO
import uuid
import os
import zipfile
import panel as pn
import panel.widgets as pw
from .config import SUBMISSION_FOLDER


class Isotherm():
    """Represents single isotherm."""
    def __init__(self, name, json, figure=None):
        self.name = name
        self.json = json
        self.figure = figure

        self.btn_remove = pw.Button(name='X', button_type='primary')
        self.btn_remove.on_click(self.on_click_remove)

        self.row = pn.GridSpec(height=35)
        self.row[0, 0:19] = pn.pane.HTML(self.name)
        self.row[0, 20] = self.btn_remove

    def on_click_remove(self, event):  # pylint: disable=unused-argument
        """Remove this adsorbent from the list."""
        self.parent.remove(self)  # pylint: disable=no-member

    @property
    def json_str(self):
        """Return json bytes string of data."""
        import json  # pylint: disable=import-outside-toplevel
        return json.dumps(self.json, indent=4)


class Submissions():
    """Stores stack of isotherms for combined submission."""
    def __init__(self):
        """Initialize empty submission."""
        self._isotherms = []

        self.btn_submit = pw.Button(name='Submit', button_type='primary')
        self.btn_submit.on_click(self.on_click_submit)

        self._column = pn.Column(objects=[a.row
                                          for a in self] + [self.btn_submit])

    @property
    def layout(self):
        """Display isotherms."""
        return self._column

    def add(self, isotherm):
        """Add isotherm to submission."""
        isotherm.parent = self
        self._isotherms.append(isotherm)
        self._column.insert(-2, isotherm.row)

    def remove(self, isotherm):
        """Remove isotherm from list."""
        self._isotherms.remove(isotherm)
        self._column.remove(isotherm.row)

    def create_zip(self):
        """Create zip file for download."""
        memfile = BytesIO()
        with zipfile.ZipFile(memfile,
                             mode='w',
                             compression=zipfile.ZIP_DEFLATED) as zhandle:
            for i, isotherm in enumerate(self):
                filename = '{}.Isotherm{}.json'.format(isotherm.json['DOI'],
                                                       i).replace('/', '')
                zhandle.writestr(filename, isotherm.json_str)

        return memfile

    def on_click_submit(self, event):  # pylint: disable=unused-argument
        """Submit stack of isotherms."""
        filename = '{}.zip'.format(uuid.uuid4())
        file_path = os.path.join(SUBMISSION_FOLDER, filename)
        memfile = self.create_zip()
        with open(file_path, 'wb') as handle:  # use `wb` mode
            handle.write(memfile.getvalue())

        print('Find zip file in {}'.format(file_path))

    def __len__(self):
        return len(self._isotherms)

    def __iter__(self):
        for elem in self._isotherms:
            yield elem

    def __getitem__(self, item):
        return self._isotherms[item]
