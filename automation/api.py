from django.http import HttpResponse

from rest_framework import authentication, permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
import logger
import threading
import os

from automation.models import Action, Alarm, Media
from automation.serializers import ActionSerializer, ActionHistorySerializer, AlarmSerializer, MediaSerializer

from raspberry.settings import AUTOMATION

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class GetActions(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        actions = Action.objects.all()
        serializer = ActionSerializer(actions, many=True)
        
        return JSONResponse(serializer.data)

class ExecuteAction(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def post(self, request, format=None):
        serializer = ActionHistorySerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            action = data["action"]
            try:
                newStatus, priority, duration = action.execute(priority=data["priority"], duration=data["duration"])
                data["status"] = newStatus
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValueError as e:
                logger.warning(e)
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAlarm(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, format=None):
        try:
            alarm = Alarm.objects.latest()
        except Alarm.DoesNotExist:
            alarm = None
        serializer = AlarmSerializer(alarm)
        
        return JSONResponse(serializer.data)

class ToggleAlarm(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
 
    def post(self, request, format=None):
        serializer = AlarmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetMedia(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, format=None):
        media = Media.objects.filter(type='video').order_by('-dateCreated')
        serializer = MediaSerializer(media, many=True)
        
        return JSONResponse(serializer.data)
    
class DeleteMedia(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
 
    def __deleteMedia(self, media, mediaPath):
        media.delete()
        os.remove("{}{}".format(mediaPath, media.fileName))

    def post(self, request, format=None):
        identifier = request.data
        [self.__deleteMedia(media, AUTOMATION['mediaPath']) for media in Media.objects.filter(identifier=identifier)]
        
        return Response(identifier, status=status.HTTP_200_OK)

class RecordVideo(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        th = threading.Thread(target=Media.recordVideo())
        th.start()

        return JSONResponse({"status": "OK", "message": "Grabación iniciada"})
