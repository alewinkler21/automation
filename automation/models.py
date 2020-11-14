from __future__ import unicode_literals

from django.db import models

class NotificationClient(models.Model):
    client_id = models.CharField(max_length=80)
    registration_id = models.TextField()
    registration_date = models.DateTimeField('registration_date', auto_now_add=True)
    registration_update = models.DateTimeField('registration_update', auto_now=True)
    device_id = models.CharField(max_length=50, primary_key=True)
    def __str__(self):
        return self.device_id
    class Meta:
        get_latest_by = 'registration_update'

class DeviceGroup(models.Model):
    name = models.CharField('Group', max_length=50, unique=True)
    def __str__(self):
        return self.name

class GPIOOutputType(models.Model):
    name = models.CharField('Type', max_length=50, unique=True)
    def __str__(self):
        return self.name

class GPIOInputType(models.Model):
    name = models.CharField('Type', max_length=50, unique=True)
    def __str__(self):
        return self.name
    
class PioneerType(models.Model):
    name = models.CharField('Type', max_length=50, unique=True)
    def __str__(self):
        return self.name

class Device(models.Model):
    name = models.CharField(max_length=50, unique=True)
    enabled = models.BooleanField(default=True)
    group = models.ForeignKey(DeviceGroup, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        abstract=True

class GPIODevice(Device):
    pinNumber = models.IntegerField('pin number');
    address = models.CharField(max_length=50, editable=False, default='127.0.0.1')
    def __str__(self):
        return self.name
    class Meta:
        abstract=True
        unique_together = ("pinNumber", "address")

class GPIOOutputDevice(GPIODevice):
    type = models.ForeignKey(GPIOOutputType, on_delete=models.CASCADE, default=0)
    autoEnabled = models.BooleanField(default=False)
    simulationEnabled = models.BooleanField(default=False)
    clapEnabled = models.BooleanField(default=False)
    longTimeStart = models.TimeField(null=True, blank=True)
    longTimeEnd = models.TimeField(null=True, blank=True)
    longTimeDuration = models.IntegerField(default=3600)
    shortTimeDuration = models.IntegerField(default=30)
    status = models.BooleanField(default=False, editable=False)

class GPIOInputDevice(GPIODevice):
    type = models.ForeignKey(GPIOInputType, on_delete=models.CASCADE, default=0)
    threshold = models.IntegerField();

class PioneerDevice(Device):
    address = models.CharField(max_length=50)
    port = models.IntegerField();
    type = models.ForeignKey(PioneerType, on_delete=models.CASCADE, default=0)

class DeviceAction(models.Model):
    dateOfUse = models.DateTimeField('date of use', auto_now_add=True)
    status = models.BooleanField()
    isAutomatic = models.BooleanField(default=False)
    class Meta:
        unique_together = ('device', 'dateOfUse')
        abstract=True

class GPIODeviceAction(DeviceAction):
    device = models.ForeignKey(GPIOOutputDevice, on_delete=models.CASCADE)
    def __str__(self):
        return 'Device: {0} | Status: {1} | isAutomatic: {2} | dateOfUse: {3}'.format(self.device.name, self.status, self.isAutomatic, self.dateOfUse.strftime("%Y-%m-%d %H:%M:%S"))

class PioneerDeviceAction(DeviceAction):
    device = models.ForeignKey(PioneerDevice, on_delete=models.CASCADE)

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