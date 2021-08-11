from django.http import HttpResponse
from django.core.paginator import Paginator

from rest_framework import authentication, permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from automation import logger
from os import remove
from automation.redis import redis
from django.db.models import Q
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
        for action in serializer.data:
            a = actions.filter(id=action["id"])[0]
            action["durationOn"] = redis.ttl(a.turnOffFlag())
            action["durationOff"] = redis.ttl(a.keepOffFlag())

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
        playMusic = redis.get("play.music")
        if playMusic is None:
            return False
        else:
            return bool(playMusic)
        
    def post(self, request, format=None):
        playMusic = not self.__continuePlaying()
        redis.set("play.music", bytes(playMusic))

        return JSONResponse(playMusic)
