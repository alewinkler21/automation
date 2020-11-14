from django.contrib import admin

# Register your models here.
from automation.models import GPIOOutputDevice, PioneerDevice, DeviceGroup, GPIOOutputType, PioneerType,\
    GPIOInputDevice, GPIOInputType

admin.site.register(GPIOOutputDevice)
admin.site.register(GPIOInputDevice)
admin.site.register(PioneerDevice)
admin.site.register(DeviceGroup)
admin.site.register(GPIOOutputType)
admin.site.register(GPIOInputType)
admin.site.register(PioneerType)