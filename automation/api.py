from django.http import HttpResponse

from rest_framework import authentication, permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import redis
import pytz
from django.utils import timezone
from datetime import datetime, timedelta
import logger

from automation.models import GPIOOutputDevice, PioneerDevice, GPIODeviceAction, PioneerDeviceAction, DeviceGroup, \
LightState, Alarm
from automation.serializers import PioneerDeviceSerializer, GPIOOutputDeviceSerializer, DeviceGroupSerializer, \
PioneeerDeviceActionSerializer, GPIODeviceActionSerializer, ListGPIODeviceActionSerializer, \
ListPioneerDeviceActionSerializer, LightSensorSerializer, NotificationClientSerializer, \
AlarmSerializer, AuthSerializer

from automation.gpio import toggle_gpio
from automation.pioneer import toggle_pioneer

timeZone = pytz.timezone("America/Montevideo")
sharedMemory = redis.Redis(host='127.0.0.1', port=6379, db=0)

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
 
class ListGroups(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        groups = DeviceGroup.objects.all()
        serializer = DeviceGroupSerializer(groups, many=True)
        return JSONResponse(serializer.data)
 
class ListPioneerDevices(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        devices = PioneerDevice.objects.filter(enabled=True)
        serializer = PioneerDeviceSerializer(devices, many=True)
        return JSONResponse(serializer.data)

class ListGPIOOutputDevices(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        devices = GPIOOutputDevice.objects.filter(enabled=True)
        serializer = GPIOOutputDeviceSerializer(devices, many=True)
        return JSONResponse(serializer.data)
    
class ListGPIODeviceActions(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        deviceActions = GPIODeviceAction.objects.order_by('-dateOfUse')[:10]
        serializer = ListGPIODeviceActionSerializer(deviceActions, many=True)
        return JSONResponse(serializer.data)

class ListPioneerDeviceActions(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        deviceActions = PioneerDeviceAction.objects.order_by('-dateOfUse')[:10]
        serializer = ListPioneerDeviceActionSerializer(deviceActions, many=True)
        return JSONResponse(serializer.data)
    
class ListLightSensor(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        lightSensor = LightState.objects.order_by('-date')[:10]
        serializer = LightSensorSerializer(lightSensor, many=True)
        return JSONResponse(serializer.data)
    
class ToggleGPIODevice(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def post(self, request, format=None):
        serializer = GPIODeviceActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.validated_data
            device = data['device']
            
            if device.address == '127.0.0.1':
                # toggle local device
                device.status = data['status']
                toggle_gpio(device.status, device.pinNumber)
                device.save()
                if device.status:
                    # set automatic turn off
                    now = datetime.now(tz=timeZone)
                    turnOffDatetime = now + timedelta(seconds=device.longTimeDuration)
                    sharedMemory.set(device.address + '-' + str(device.id), str(turnOffDatetime))
                    logger.debug("WebAPI: Set automatic turn off for device: {} Off: {}".format(device.name,
                                                                                                turnOffDatetime.strftime("%Y-%m-%d %H:%M:%S")))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # toggle remote device
                url = 'http://{}{}'.format(device.address, request.path)
                resp = requests.get(url, headers=request.headers, verify=False)
                if resp.status_code == 201:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(resp.reason, status=resp.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TogglePioneerDevice(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def post(self, request, format=None):
        serializer = PioneeerDeviceActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.validated_data
            device = data['device']            
            if not toggle_pioneer(data['status'], device):
                return Response(serializer.data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            device.status = data['status']
            device.save()
#             if a pioneer device is turned on, turn off others
            if device.status:
                others = PioneerDevice.objects.exclude(id=device.id)
                for o in others:
                    o.status = False
                    o.save()
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RegisterNotificationClient(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def post(self, request, format=None):
        serializer = NotificationClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetAlarm(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, format=None):
        alarm = Alarm.objects.last()
        serializer = AlarmSerializer(alarm)
        return JSONResponse(serializer.data)

class ToggleAlarm(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def post(self, request, format=None):
        serializer = AlarmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAuthToken(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, format=None):
        serializer = AuthSerializer(request.user, many=False)
        return JSONResponse(serializer.data)