from __future__ import unicode_literals

from django.db import models

class DeviceGroup(models.Model):
    name = models.CharField('Group', max_length=50, unique=True)
    def __str__(self):
        return self.name

class Device(models.Model):
    name = models.CharField(max_length=50, unique=True)
    enabled = models.BooleanField(default=True)
    group = models.ForeignKey(DeviceGroup, on_delete=models.CASCADE)
    address = models.CharField(max_length=50, editable=False, default='127.0.0.1')
    def __str__(self):
        return self.name
    class Meta:
        abstract=True

class GPIODevice(Device):
    pinNumber = models.IntegerField('pin number');
    def __str__(self):
        return self.name
    class Meta:
        abstract=True
        unique_together = ("pinNumber", "address")

class Led(GPIODevice):
    pass
    
class Relay(GPIODevice):
    autoEnabled = models.BooleanField(default=False)
    longTimeStart = models.TimeField()
    longTimeEnd = models.TimeField()
    longTimeDuration = models.IntegerField(default=3600)
    shortTimeDuration = models.IntegerField(default=30)
    status = models.BooleanField(default=False, editable=False)

class LightSensor(GPIODevice):
    threshold = models.IntegerField();

class PirSensor(GPIODevice):
    led = models.ForeignKey(Led, on_delete=models.CASCADE, null=True, blank=True)
    checkLighting = models.BooleanField(default=True)
    
class RelayAction(models.Model):
    relay = models.ForeignKey(Relay, on_delete=models.CASCADE)
    dateOfUse = models.DateTimeField('date of use', auto_now_add=True)
    status = models.BooleanField()
    isAutomatic = models.BooleanField(default=False)
    class Meta:
        unique_together = ('relay', 'dateOfUse')
    def __str__(self):
        return 'Device: {0} | Status: {1} | isAutomatic: {2} | dateOfUse: {3}'.format(self.relay.name, self.status, self.isAutomatic, self.dateOfUse.strftime("%Y-%m-%d %H:%M:%S"))

class LightState(models.Model):
    date = models.DateTimeField('date', auto_now_add=True)
    brightness = models.IntegerField();
    isDark = models.BooleanField()
    class Meta:
        unique_together = ('date', 'isDark')
        get_latest_by = 'date'

class Alarm(models.Model):
    armed = models.BooleanField(default=False)
    fired = models.BooleanField(default=False)
    eventDate = models.DateTimeField('event date', auto_now_add=True, null=True, blank=True)
    useCamera = models.BooleanField(default=False)
    detectPeople = models.BooleanField(default=False)

class Media(models.Model):
    identifier = models.CharField(max_length=50)
    dateCreated = models.DateTimeField('date created', auto_now_add=True)
    fileName = models.CharField(max_length=50)
    type = models.CharField(max_length=5, null=True)
    triggeredByAlarm = models.BooleanField(default=False)
    peopleDetected = models.BooleanField(default=False)

