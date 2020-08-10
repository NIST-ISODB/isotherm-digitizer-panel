"""Dynamic list of adsorbates."""
import panel as pn
import panel.widgets as pw
from .config import QUANTITIES

class Adsorbate():
    """Input form for describing adsorbates."""

    def __init__(self, parent):
        """Initialize single adsorbent row.

        :param parent: Adsorbates instance
        """
        self.parent = parent
        self.inp_name = pw.AutocompleteInput(name='Adorbate Gas/Fluid', placeholder='Methane',
                                             options=QUANTITIES['adsorbates']['names'], css_classes = ['required'])
        self.btn_add = pw.Button(name='+', button_type='primary')
        self.btn_add.on_click(self.on_click_add)
        self.btn_remove = pw.Button(name='-', button_type='primary')
        self.btn_remove.on_click(self.on_click_remove)
        #self.inp_refcode = pw.TextInput(name='Refcode')
        #self.row = pn.Row(self.inp_name, self.btn_add, self.btn_remove)
        self.row = pn.GridSpec(height=50)
        self.row[0,0:8] = self.inp_name
        self.row[0,8] = self.btn_add
        self.row[0,9] = self.btn_remove

    def on_click_add(self, event):
        self.parent.add(Adsorbate(parent=self.parent))

    def on_click_remove(self, event):
        self.parent.remove(self)

    @property
    def dict(self):
        """Dictionary with adsorbate info"""
        return { 'name': self.inp_name.value }

class Adsorbates():
    """List of all adsorbates"""

    def __init__(self, adsorbates=None, required_inputs=None):
        """
        Create dynamic list of adsorbates.

        :param adsorbates: List of adsorbate entities to prepopulate (optional)
        :param required_inputs: List of required inputs to keep updated (optional)
        """
        self._adsorbates = adsorbates or []
        self._column = pn.Column(objects=[a.row for a in self])
        self._required_inputs = required_inputs

        # Add one adsorbate
        if not self._adsorbates:
            self.add(Adsorbate(parent=self))

    @property
    def column(self):
        return self._column

    @property
    def dict(self):
        """Dictionary with adsorbate info"""
        return [ a.dict for a in self ]

    def add(self, adsorbate):
        """Add new adsorbate."""
        self._adsorbates.append(adsorbate)
        self._column.append(adsorbate.row)
        if self._required_inputs is not None:
            self._required_inputs.append(adsorbate.inp_name)

    def remove(self, adsorbate):
        """Remove adsorbate from list."""
        self._adsorbates.remove(adsorbate)
        self._column.remove(adsorbate.row)
        if self._required_inputs:
            self._required_inputs.remove(adsorbate.inp_name)

    def __iter__(self):
        for elem in self._adsorbates:
            yield elem

    def __len__(self):
        return len(self._adsorbates)