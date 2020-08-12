# -*- coding: utf-8 -*-
"""Dynamic list of adsorbates."""
import panel as pn
import panel.widgets as pw
from .config import QUANTITIES


class Adsorbate():  # pylint: disable=too-few-public-methods
    """Input form for describing adsorbates."""
    def __init__(self):
        """Initialize single adsorbent row.
        """
        self.inp_name = pw.AutocompleteInput(
            name='Adorbate Gas/Fluid',
            placeholder='Methane',
            options=QUANTITIES['adsorbates']['names'],
            css_classes=['required'])
        self.row = pn.Row(self.inp_name)

    @property
    def dict(self):
        """Dictionary with adsorbate info"""
        return {'name': self.inp_name.value}


class AdsorbateWithControls(Adsorbate):
    """Input form for describing adsorbates with controls to add/remove them."""
    def __init__(self, parent):
        """Initialize single adsorbent row.

        :param parent: Adsorbates instance
        """
        super().__init__()
        self.parent = parent
        self.btn_add = pw.Button(name='+', button_type='primary')
        self.btn_add.on_click(self.on_click_add)
        self.btn_remove = pw.Button(name='-', button_type='primary')
        self.btn_remove.on_click(self.on_click_remove)
        #self.inp_refcode = pw.TextInput(name='Refcode')
        #self.row = pn.Row(self.inp_name, self.btn_add, self.btn_remove)
        self.row = pn.GridSpec(height=50)
        self.row[0, 0:8] = self.inp_name
        self.row[0, 8] = self.btn_add
        self.row[0, 9] = self.btn_remove

    def on_click_add(self, event):  # pylint: disable=unused-argument
        """Add new adsorbate."""
        self.parent.add(AdsorbateWithControls(parent=self.parent))

    def on_click_remove(self, event):  # pylint: disable=unused-argument
        """Remove this adsorbent from the list."""
        self.parent.remove(self)


class Adsorbates():
    """List of all adsorbates"""
    def __init__(self, adsorbates=None, show_controls=True):
        """
        Create dynamic list of adsorbates.

        :param adsorbates: List of adsorbate entities to prepopulate (optional)
        :param show_controls: Whether to display controls for addin/removing adsorbents.
        """
        self._adsorbates = adsorbates or []
        self._column = pn.Column(objects=[a.row for a in self])

        # Add one adsorbate
        if not self._adsorbates:
            if show_controls:
                self.add(AdsorbateWithControls(parent=self))
            else:
                self.add(Adsorbate())

    @property
    def column(self):
        """Panel column for visualization"""
        return self._column

    @property
    def inputs(self):
        """List of inputs"""
        return [a.inp_name for a in self]

    def add(self, adsorbate):
        """Add new adsorbate."""
        self._adsorbates.append(adsorbate)
        self._column.append(adsorbate.row)

    def remove(self, adsorbate):
        """Remove adsorbate from list."""
        self._adsorbates.remove(adsorbate)
        self._column.remove(adsorbate.row)

    def __iter__(self):
        for elem in self._adsorbates:
            yield elem

    def __len__(self):
        return len(self._adsorbates)
