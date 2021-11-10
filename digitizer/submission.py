# -*- coding: utf-8 -*-
"""Store stack of submissions"""
from io import BytesIO
import uuid
import os
import zipfile
from traitlets import HasTraits, Instance
import pydenticon

import panel as pn
import panel.widgets as pw

from .config import SUBMISSION_FOLDER

ROW_HEIGHT = 35  # pixel
PYDENTICON_GENERATOR = pydenticon.Generator(5, 5)


class Isotherm(HasTraits):
    """Represents single isotherm."""
    def __init__(self, json, figure_image=None, name=None):
        super().__init__()
        self.parent = None
        self.json = json
        self.figure_image = figure_image
        self.name = name or '{} ({})'.format(json['articleSource'], json['DOI'])

        self.btn_remove = pw.Button(name='❌', button_type='primary')
        self.btn_remove.on_click(self.on_click_remove)

        self.btn_load = pw.Button(name='📂', button_type='primary')
        self.btn_load.on_click(self.on_click_load)

        row = pn.GridSpec(height=ROW_HEIGHT)
        row[0, 0:17] = pn.pane.HTML(self.name)
        row[0, 18] = pn.pane.PNG(object=get_identicon(str(hash(self))))
        row[0, 19] = self.btn_load
        row[0, 20] = self.btn_remove
        self.row = row

    def on_click_remove(self, event):  # pylint: disable=unused-argument
        """Remove this adsorbent from the list."""
        self.parent.remove(self)  # pylint: disable=no-member

    def on_click_load(self, event):  # pylint: disable=unused-argument
        """Load data from this isotherm."""
        self.parent.loaded_isotherm = self

    @property
    def json_str(self):
        """Return json bytes string of data."""
        import json  # pylint: disable=import-outside-toplevel
        return json.dumps(self.json, ensure_ascii=False, sort_keys=True, indent=4)

    def __hash__(self):
        return hash(str(self.json))


class Submissions(HasTraits):  # pylint: disable=R0901
    """Stores stack of isotherms for combined submission.

    The Submissions.loaded_isotherm trait can be observed in order to react to changes::

        def on_load(change):
            ...

        s = Submissions()
        s.observed_forms(on_change, names=['loaded_isotherm'])


    """

    loaded_isotherm = Instance(Isotherm)

    def __init__(self):
        """Initialize empty submission."""
        super().__init__()
        self.data = []

        self.btn_submit = pw.Button(name='Submit', button_type='primary')
        self.btn_submit.on_click(self.on_click_submit)

        self.btn_download = pn.widgets.FileDownload(filename='submission.zip',
                                                    button_type='primary',
                                                    callback=self.on_click_download)
        self.btn_download.data = ''  # bug in panel https://github.com/holoviz/panel/issues/1598
        self._submit_btns = pn.Row(self.btn_download, self.btn_submit)

        self._column = pn.Column(objects=[a.row for a in self])

    @property
    def layout(self):
        """Display isotherms."""
        return self._column

    def append(self, isotherm):  # pylint: disable=W0221
        """Add isotherm to submission.

        Note: For better usability, we append *on top*.
        """
        if isotherm in self.data:
            print('Isotherm already added')
            return

        isotherm.parent = self
        self.data.insert(0, isotherm)

        if len(self) == 1:
            # we now need submit buttons
            self._column.insert(-1, self._submit_btns)

        self._column.insert(0, isotherm.row)

    def remove(self, isotherm):  # pylint: disable=W0221
        """Remove isotherm from list."""
        self.data.remove(isotherm)

        if len(self) == 0:
            # we should remove submit buttons
            self._column.pop(-1)
        self._column.remove(isotherm.row)

    def get_zip_file(self):
        """Create zip file for download."""
        memfile = BytesIO()
        with zipfile.ZipFile(memfile, mode='w', compression=zipfile.ZIP_DEFLATED) as zhandle:

            isotherm_counters = {}

            for isotherm in self:
                doi = isotherm.json['DOI']
                directory = doi.replace('/', '')

                if doi not in isotherm_counters:
                    isotherm_counters[doi] = 1

                if isotherm.figure_image:
                    filename = '{d}/{d}.Isotherm{i}_{f}'.format(d=directory,
                                                                i=isotherm_counters[doi],
                                                                f=isotherm.figure_image.filename)
                    isotherm.json['associated_content'] = [filename]
                    zhandle.writestr(filename, isotherm.figure_image.data)

                filename = '{d}/{d}.Isotherm{i}.json'.format(d=directory, i=isotherm_counters[doi])
                zhandle.writestr(filename, isotherm.json_str)
                isotherm_counters[doi] += 1

        memfile.seek(0)
        return memfile

    def on_click_submit(self, event):  # pylint: disable=unused-argument
        """Submit stack of isotherms."""
        filename = '{}.zip'.format(uuid.uuid4())
        file_path = os.path.join(SUBMISSION_FOLDER, filename)
        memfile = self.get_zip_file()
        with open(file_path, 'wb') as handle:  # use `wb` mode
            handle.write(memfile.getvalue())

        print('Find zip file in {}'.format(file_path))

    def on_click_download(self):
        """Download zip file."""
        return self.get_zip_file()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        return self.data[item]


class Identicon:  # pylint: disable=too-few-public-methods
    """Wrapper for identicon for usage in pn.pane.PNG"""
    def __init__(self, image):
        self.image = image

    def _repr_png_(self):
        """Return PNG representation"""
        return self.image


def get_identicon(string):
    """Return unique PNG for given string

    :param string:  String to compute identicon for.
    :returns: base64-encoded PNG
    """
    return Identicon(image=PYDENTICON_GENERATOR.generate(string, ROW_HEIGHT, ROW_HEIGHT, output_format='png'))
