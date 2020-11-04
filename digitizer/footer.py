# -*- coding: utf-8 -*-
"""Footer with logos from supporters."""
import os
import panel as pn

from . import TEMPLATES_DIR

with open(os.path.join(TEMPLATES_DIR, 'footer.html')) as handle:
    footer = pn.pane.HTML(handle.read(), width=940)
