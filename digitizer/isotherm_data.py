# -*- coding: utf-8 -*-
"""Input Boxes for Isotherm Data."""
import collections
import panel as pn
import panel.widgets as pw
from .config import MULTI_COMPONENT_EXAMPLE, SINGLE_COMPONENT_EXAMPLE


class IsothermData():
    """Input form for an isotherm data block."""
    def __init__(self, parent, multicomp=False, ads_branch=True):
        """Initialize single isotherm data block [i.e., one branch]."""
        self.multicomp = multicomp
        if self.multicomp:
            placeholder = MULTI_COMPONENT_EXAMPLE
            width = 450  # this is arbitrary
        else:
            placeholder = SINGLE_COMPONENT_EXAMPLE
            width = 250  # this is arbitrary

        if ads_branch:
            name = 'Isotherm Data (Adsorption Branch)'
        else:
            name = 'Isotherm Data (Desorption Branch)'
        self.inp_name = pw.TextAreaInput(name=name, height=200, width=width, placeholder=placeholder)

        self.parent = parent
        self.btn_add = pw.Button(name='+', button_type='primary')
        self.btn_add.on_click(self.on_click_add)
        self.btn_remove = pw.Button(name='-', button_type='primary')
        self.btn_remove.on_click(self.on_click_remove)
        if ads_branch:
            self.row = pn.GridSpec(height=200)
            self.row[0, 0:8] = self.inp_name
            self.row[0, 8] = self.btn_add
        else:
            self.row = pn.GridSpec(height=200)
            self.row[0, 0:8] = self.inp_name
            self.row[0, 8] = self.btn_remove

    def on_click_add(self, event):  # pylint: disable=unused-argument
        """Add Desorption Isotherm Data Block."""
        self.parent.append(IsothermData(parent=self.parent, multicomp=self.multicomp, ads_branch=False))

    def on_click_remove(self, event):  # pylint: disable=unused-argument
        """Remove this Isotherm Data Block."""
        self.parent.remove(self)

    @property
    def value(self):
        """Return the text content of the TextAreaInput."""
        return self.inp_name.value


class IsothermDataBlocks(collections.UserList):  # pylint: disable=R0901
    """List of all adsorbates"""
    def __init__(self, multicomp=False):
        """
        Create dynamic list of isotherm data blocks.

        Note: This class inherits from collections.UserList for automatic implementation of len() and the subscript
         operator. The internal list is stored in self.data.
        """
        super().__init__()
        self.data = []
        self._column = pn.Column(objects=[a.row for a in self])

        # Add one adsorbate
        if not self.data:
            self.append(IsothermData(parent=self, multicomp=multicomp, ads_branch=True))

    @property
    def column(self):
        """Panel column for visualization"""
        return self._column

    @property
    def inputs(self):
        """List of inputs"""
        return [a.inp_name for a in self]

    def append(self, branch):  # pylint: disable=W0221
        """Add a desorption data branch."""
        self.data.append(branch)
        self._column.append(branch.row)

    def remove(self, branch):  # pylint: disable=W0221
        """Remove desorption data branch."""
        self.data.remove(branch)
        self._column.remove(branch.row)
