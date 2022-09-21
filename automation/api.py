from django.http import HttpResponse
from django.core.paginator import Paginator

from rest_framework import authentication, permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from automation import logger
from os import listdir, remove
from automation.redis import redis_conn
from django.db.models import Q
from automation.models import Action, Alarm, Media, LightSensor, ActionHistory
from automation.serializers import ActionSerializer, ActionHistorySerializer, GetActionHistorySerializer, AlarmSerializer, MediaSerializer

from raspberry.settings import AUTOMATION
import subprocess

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
        for action in serializer.data:
            a = actions.filter(id=action["id"])[0]
            action["durationOn"] = redis_conn.ttl(a.turnOffFlag())
            action["durationOff"] = redis_conn.ttl(a.keepOffFlag())

        return JSONResponse(serializer.data)

class GetActionsHistory(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        actionsHistory = ActionHistory.objects.all().order_by('-date')[:15]
        serializer = GetActionHistorySerializer(actionsHistory, many=True)

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
                newStatus, priority, duration = action.execute(priority=data["priority"], duration=data["duration"], who=data["who"])
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
        last = Media.objects.last()
        lastId = last.id if last else 0
        media = Media.objects.filter(Q(movementDetected=True) | Q(id=lastId)).order_by('-dateCreated')
#         paginator = Paginator(media, 5)
#         page = paginator.get_page(1)
#         serializer = MediaSerializer(page, many=True)
        serializer = MediaSerializer(media, many=True)
        
        return JSONResponse(serializer.data)

class DeleteMedia(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
 
    def __deleteMedia(self, media):
        media.delete()
        remove("{}{}".format(AUTOMATION['mediaPath'], media.videoFile))

    def post(self, request, format=None):
        media = Media.objects.get(id=request.data)
        if media:
            self.__deleteMedia(media)
            
        return Response(request.data, status=status.HTTP_200_OK)
    
class PlayMusic(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    
    def __continuePlaying(self):
        playMusic = redis_conn.get("play.music")
        if playMusic is None:
            return False
        else:
            return bool(playMusic)
        
    def post(self, request, format=None):
        playMusic = not self.__continuePlaying()
        redis_conn.set("play.music", bytes(playMusic))

        return JSONResponse(playMusic)
    
class SystemStatus(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, request, format=None):
        uptime = subprocess.run(["uptime", "-p"], capture_output=True)
        temp = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
        isDark = True
        lightSensor = LightSensor.objects.first()
        if lightSensor:
            isDark = lightSensor.getDarkness()

        data = {}
        data["uptime"] = str(uptime.stdout, "UTF-8").rstrip()
        data["temperature"] = str(temp.stdout, "UTF-8").rstrip()
        data["isDark"] = isDark
        
        return JSONResponse(data)
    
class GetPhotos(APIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
 
    def get(self, format=None):
        photos = []
        for f in listdir(AUTOMATION["mediaPath"]):
            photos.append(f)
                
        return JSONResponse(photos)
