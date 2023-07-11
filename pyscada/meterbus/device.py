# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from time import time, sleep

from pyscada.device import GenericDevice
from .devices import GenericDevice as GenericHandlerDevice

import logging

logger = logging.getLogger(__name__)

try:
    import meterbus

    driver_ok = True
except ImportError:
    logger.error("Cannot import meterbus")
    driver_ok = False


class Device(GenericDevice):
    """
    MeterBus device
    """

    def __init__(self, device):
        self.driver_ok = driver_ok
        self.handler_class = GenericHandlerDevice
        super().__init__(device)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, "meterbusvariable"):
                continue
            self.variables[var.pk] = var

        if self.driver_ok and self.driver_handler_ok:
            if not self._h.connect():
                sleep(60)
                self._h.connect()

        self._h.accessibility()

    def request_data(self):
        if driver_ok and self.driver_handler_ok and self._h.inst is None:
            self._h.connect()
            self._h.accessibility()

        output = super().request_data()

        return output
