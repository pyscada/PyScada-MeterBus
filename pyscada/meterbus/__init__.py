# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pyscada

__version__ = "0.8.0"
__author__ = "Camille Lavayssiere"
__email__ = "team@pyscada.org"
__description__ = (
    "Meterbus extension for PyScada a Python and Django based Open Source SCADA System"
)
__app_name__ = "Meterbus"

PROTOCOL_ID = 15

parent_process_list = [
    {
        "pk": PROTOCOL_ID,
        "label": "pyscada." + __app_name__.lower(),
        "process_class": "pyscada." + __app_name__.lower() + ".worker.Process",
        "process_class_kwargs": '{"dt_set":30}',
        "enabled": True,
    }
]
