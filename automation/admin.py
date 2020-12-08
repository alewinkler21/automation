from django.contrib import admin

# Register your models here.
from automation.models import Relay, DeviceGroup, PirSensor, LightSensor, Led

admin.site.register(DeviceGroup)
admin.site.register(Relay)
admin.site.register(PirSensor)
admin.site.register(LightSensor)
admin.site.register(Led)