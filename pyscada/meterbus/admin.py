# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.meterbus import PROTOCOL_ID
from pyscada.meterbus.models import MeterBusDevice, ExtendedMeterBusDevice
from pyscada.meterbus.models import MeterBusVariable, ExtendedMeterBusVariable
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol
from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class MeterBusDeviceAdminInline(admin.StackedInline):
    model = MeterBusDevice


class MeterBusDeviceAdmin(DeviceAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(MeterBusDeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(MeterBusDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        MeterBusDeviceAdminInline
    ]


class MeterBusVariableAdminInline(admin.StackedInline):
    model = MeterBusVariable


class MeterBusVariableAdmin(VariableAdmin):
    list_display = ('id', 'name', 'description', 'unit', 'device_name', 'value_class', 'active', 'writeable')
    list_editable = ('active', 'writeable',)
    list_display_links = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(MeterBusVariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(MeterBusVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        MeterBusVariableAdminInline
    ]


# admin_site.register(ExtendedSerialDevice, SerialDeviceAdmin)
# admin_site.register(ExtendedSerialVariable, SerialVariableAdmin)
