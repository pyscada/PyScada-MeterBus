# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.meterbus.models import MeterBusDevice, MeterBusVariable, ExtendedMeterBusVariable, \
    ExtendedMeterBusDevice

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=MeterBusDevice)
@receiver(post_save, sender=MeterBusVariable)
@receiver(post_save, sender=ExtendedMeterBusVariable)
@receiver(post_save, sender=ExtendedMeterBusDevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is MeterBusDevice:
        post_save.send_robust(sender=Device, instance=instance.meterbus_device)
    elif type(instance) is MeterBusVariable:
        post_save.send_robust(sender=Variable, instance=instance.meterbus_device)
    elif type(instance) is ExtendedMeterBusVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedMeterBusDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
