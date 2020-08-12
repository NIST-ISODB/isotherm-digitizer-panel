# -*- coding: utf-8 -*-
"""Dynamic list of adsorbates."""
import collections
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
    """Input form for describing adsorbates with controls to append/remove them."""
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
        self.parent.append(AdsorbateWithControls(parent=self.parent))

    def on_click_remove(self, event):  # pylint: disable=unused-argument
        """Remove this adsorbent from the list."""
        self.parent.remove(self)


class Adsorbates(collections.UserList):  # pylint: disable=R0901
    """List of all adsorbates"""
    def __init__(self, adsorbates=None, show_controls=True):
        """
        Create dynamic list of adsorbates.

        :param adsorbates: List of adsorbate entities to prepopulate (optional)
        :param show_controls: Whether to display controls for addin/removing adsorbents.

        Note: This class inherits from collections.UserList for automatic implementation of len() and the subscript
         operator. The internal list is stored in self.data.
        """
        super().__init__()
        self.data = adsorbates or []
        self._column = pn.Column(objects=[a.row for a in self])

        # Add one adsorbate
        if not self.data:
            if show_controls:
                self.append(AdsorbateWithControls(parent=self))
            else:
                self.append(Adsorbate())

    @property
    def column(self):
        """Panel column for visualization"""
        return self._column

    @property
    def inputs(self):
        """List of inputs"""
        return [a.inp_name for a in self]

    def append(self, adsorbate):  # pylint: disable=W0221
        """Add new adsorbate."""
        self.data.append(adsorbate)
        self._column.append(adsorbate.row)

    def remove(self, adsorbate):  # pylint: disable=W0221
        """Remove adsorbate from list."""
        self.data.remove(adsorbate)
        self._column.remove(adsorbate.row)
