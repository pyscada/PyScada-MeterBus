# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, DeviceHandler
from pyscada.models import Variable
from . import PROTOCOL_ID

import meterbus

from django.db import models
import logging

logger = logging.getLogger(__name__)


class MeterBusDevice(models.Model):
    meterbus_device = models.OneToOneField(
        Device, null=True, blank=True, on_delete=models.CASCADE
    )
    address = models.PositiveSmallIntegerField(
        default=0,
    )
    address_type_choices = (
        (1, "primary"),
        (2, "secondary"),
    )
    address_type = models.PositiveSmallIntegerField(
        default=address_type_choices[0][0], choices=address_type_choices
    )
    port = models.CharField(
        default="/dev/ttyUSB0",
        max_length=400,
        help_text="enter serial port (/dev/pts/13))",
    )
    baudrate = models.PositiveIntegerField(
        default=9600, help_text="Serial connection baudrate"
    )
    timeout = models.PositiveIntegerField(
        default=1, help_text="Serial connection timeout"
    )
    retries = models.PositiveIntegerField(
        default=5, help_text="Serial connection retries"
    )
    read_and_ignore_echo = models.BooleanField(
        default=False, help_text="Read and ignore echoed data from target"
    )

    protocol_id = PROTOCOL_ID

    def parent_device(self):
        try:
            return self.meterbus_device
        except:
            return None

    def __str__(self):
        return self.meterbus_device.short_name


class MeterBusVariable(models.Model):
    meterbus_variable = models.OneToOneField(
        Variable, null=True, blank=True, on_delete=models.CASCADE
    )
    storage_number = models.PositiveSmallIntegerField(
        default=0,
        help_text="Look at the <a href='https://m-bus.com/documentation-wired/06-application-layer'>M-Bus documentation</a>",
    )

    function_choices = [(tag.value, tag) for tag in meterbus.core_objects.FunctionType]
    function = models.PositiveSmallIntegerField(default=0, choices=function_choices)

    type_choices = [(tag.value, tag) for tag in meterbus.core_objects.VIFUnit]
    type_choices.extend([(tag.value, tag) for tag in meterbus.core_objects.VIFUnitExt])
    type_choices.extend(
        [(tag.value, tag) for tag in meterbus.core_objects.VIFUnitSecExt]
    )
    type = models.PositiveSmallIntegerField(choices=type_choices)

    unit_choices = [(tag.value, tag.value) for tag in meterbus.core_objects.MeasureUnit]
    unit = models.CharField(choices=unit_choices, max_length=50)

    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Item order in data if various items with the same description",
    )

    protocol_id = PROTOCOL_ID

    def __str__(self):
        return self.id.__str__() + "-" + self.meterbus_variable.name


class ExtendedMeterBusDevice(Device):
    class Meta:
        proxy = True
        verbose_name = "MeterBus Device"
        verbose_name_plural = "MeterBus Devices"


class ExtendedMeterBusVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = "MeterBus Variable"
        verbose_name_plural = "MeterBus Variables"
