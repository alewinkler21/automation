from rest_framework import serializers
from automation.models import Device, GPIOOutputDevice, PioneerDevice, GPIODeviceAction, PioneerDeviceAction, \
DeviceGroup, GPIOOutputType, PioneerType, LightState, NotificationClient, Alarm
from django.contrib.auth.models import User

class DeviceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceGroup
        fields = ('id', 'name')

class GPIOOutputTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPIOOutputType
        fields = ('id', 'name')

class PioneerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PioneerType
        fields = ('id', 'name')
                                 
class DeviceSerializer(serializers.ModelSerializer):
    group = DeviceGroupSerializer(many=False, read_only=True)
    class Meta:
        model = Device
        fields = ()

class PioneerDeviceSerializer(DeviceSerializer):
    type = PioneerTypeSerializer(many=False, read_only=True)
    class Meta:
        model = PioneerDevice
        fields = ('id', 'name', 'enabled', 'group', 'type', 'autoEnabled', 'simulationEnabled', 'clapEnabled', 'longTimeStart', 'longTimeEnd', 'status', 'address', 'port')

class GPIOOutputDeviceSerializer(DeviceSerializer):
    type = GPIOOutputTypeSerializer(many=False, read_only=True)
    class Meta:
        model = GPIOOutputDevice
        fields = ('id', 'name', 'enabled', 'group', 'type', 'autoEnabled', 'simulationEnabled', 'clapEnabled', 'longTimeStart', 'longTimeEnd', 'status', 'pinNumber', 'address')

class ListGPIODeviceActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPIODeviceAction
        fields = ('id', 'dateOfUse', 'status', 'isAutomatic')

class GPIODeviceActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPIODeviceAction
        fields = ('id', 'device', 'dateOfUse', 'status', 'isAutomatic')

class ListPioneerDeviceActionSerializer(serializers.ModelSerializer):
    device = PioneerDeviceSerializer(many=False, read_only=True)
    class Meta:
        model = PioneerDeviceAction
        fields = ('id', 'device', 'dateOfUse', 'status', 'isAutomatic')
                
class PioneeerDeviceActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PioneerDeviceAction
        fields = ('id', 'device', 'dateOfUse', 'status', 'isAutomatic')
        
class LightSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = LightState
        fields = ('id','date', 'brightness', 'isDark')

class AlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields = ('id', 'armed', 'fired', 'eventDate')

class NotificationClientSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=80)
    registration_id = serializers.CharField()
    device_id = serializers.CharField(max_length=50)
    
    def create(self, validated_data):
        notificationClient, created = NotificationClient.objects.update_or_create(
            pk=validated_data.get('device_id', None),
            defaults=validated_data)
        return notificationClient
        
class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'auth_token')