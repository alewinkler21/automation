from rest_framework import serializers
from automation.models import GPIODevice, Relay, DeviceGroup, Alarm, RelayAction,\
    Media
from django.contrib.auth.models import User

class DeviceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceGroup
        fields = ('id', 'name')
                                 
class GPIODeviceSerializer(serializers.ModelSerializer):
    group = DeviceGroupSerializer(many=False, read_only=True)
    class Meta:
        model = GPIODevice
        abstract=True

class RelaySerializer(GPIODeviceSerializer):
    class Meta:
        model = Relay
        fields = ('id', 'name', 'enabled', 'group', 'pinNumber', 'address', 'status')
        
class RelayActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelayAction
        fields = ('id', 'relay', 'dateOfUse', 'status', 'isAutomatic')
        
class AlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields = ('armed', 'fired', 'useCamera')
        
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('id', 'identifier', 'dateCreated', 'fileName', 'type', 'triggeredByAlarm')

class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'auth_token')