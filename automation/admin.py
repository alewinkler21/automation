from django.contrib import admin

from automation.models import Relay, Action,Switch, Clock, LightSensor, PIRSensor, Raspi

admin.site.register(Raspi)
admin.site.register(Relay)
admin.site.register(Action)
admin.site.register(Switch)
admin.site.register(Clock)
admin.site.register(LightSensor)
admin.site.register(PIRSensor)