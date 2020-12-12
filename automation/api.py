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
import threading
from picamera import PiCamera, PiCameraMMALError
import time
import subprocess
import os
import sys

from automation.models import Relay, DeviceGroup, Alarm, Media
from automation.serializers import DeviceGroupSerializer, RelaySerializer, AuthSerializer, AlarmSerializer,\
    RelayActionSerializer, MediaSerializer
from automation.gpio import toggle_gpio

timeZone = pytz.timezone("America/Montevideo")
sharedMemory = redis.Redis(host='127.0.0.1', port=6379, db=0)
mediaPath = "/var/www/html/camera/"

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
 
class ListRelays(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        devices = Relay.objects.filter(enabled=True)
        serializer = RelaySerializer(devices, many=True)
        return JSONResponse(serializer.data)
    
class ToggleRelay(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def post(self, request, format=None):
        serializer = RelayActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.validated_data
            relay = data['relay']
            
            if relay.address == '127.0.0.1':
                # toggle local relay
                relay.status = data['status']
                toggle_gpio(relay.status, relay.pinNumber)
                relay.save()
                if relay.status:
                    # set automatic turn off
                    now = datetime.now(tz=timeZone)
                    turnOffDatetime = now + timedelta(seconds=relay.longTimeDuration)
                    sharedMemory.set(relay.address + '-' + str(relay.id), str(turnOffDatetime))
                    logger.debug("WebAPI: Set automatic turn off for relay: {} Off: {}".format(relay.name,
                                                                                                turnOffDatetime.strftime("%Y-%m-%d %H:%M:%S")))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # toggle remote relay
                url = 'http://{}{}'.format(relay.address, request.path)
                resp = requests.get(url, headers=request.headers, verify=False)
                if resp.status_code == 201:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(resp.reason, status=resp.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAlarm(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, format=None):
        alarm = Alarm.objects.last()
        serializer = AlarmSerializer(alarm)
        return JSONResponse(serializer.data)

class ToggleAlarm(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
 
    def post(self, request, format=None):
        serializer = AlarmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetMedia(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, format=None):
        media = Media.objects.filter(type='video').order_by('-dateCreated')
        serializer = MediaSerializer(media, many=True)
        return JSONResponse(serializer.data)

class GetAuthToken(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, format=None):
        serializer = AuthSerializer(request.user, many=False)
        return JSONResponse(serializer.data)
    
class RecordVideo(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def saveMedia(self, identifier, dateCreated, fileName, mediaType):
        media = Media()
        media.identifier = identifier
        media.dateCreated = dateCreated
        media.fileName = fileName
        media.type = mediaType
        media.triggeredByAlarm = False
        media.save() 
        
    def recordVideo(self):
        dateCreated = datetime.now(tz=timeZone)
        identifier = dateCreated.strftime("%Y_%m_%d_%H_%M_%S")
        with PiCamera() as camera:
            try:
                # photos
                for i in range(3):
                    fileName = "{}-{}.jpg".format(identifier, i)
                    logger.debug("Take picture {}".format(fileName))
                    camera.capture("{}{}".format(mediaPath, fileName))
                    self.saveMedia(identifier, dateCreated, fileName, "image")
                    time.sleep(1)
                # video
                logger.debug("Start recording video")
                fileNameH264 = "{}.h264".format(identifier)
                fileNameMP4 = "{}.mp4".format(identifier)
                camera.start_recording("{}{}".format(mediaPath, fileNameH264))
                camera.wait_recording(15)
                camera.stop_recording()
                logger.debug("Stop recording video and release camera")
                subprocess.run(["MP4Box", "-add", "{}{}".format(mediaPath, fileNameH264), "{}{}".format(mediaPath, fileNameMP4)], stdout=subprocess.DEVNULL)
                self.saveMedia(identifier, dateCreated, fileNameMP4, "video")
                os.remove("{}{}".format(mediaPath, fileNameH264))
            except PiCameraMMALError as error:
                logger.error(error)
            except:
                print("Unexpected error:", sys.exc_info()[0])

    def post(self, request, format=None):
        th = threading.Thread(target=self.recordVideo)
        th.start()
        return Response("OK", status=status.HTTP_200_OK)
