from django.db import models
from django.utils import timezone
import pytz
from datetime import datetime, timedelta
from automation.gpio import toggleGPIO
import redis
import logger
import uuid
import subprocess
import os
import sys
import requests
#from picamera import PiCamera, PiCameraMMALError

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

class Raspi(models.Model):
    address = models.CharField(max_length=50, default="127.0.0.1")
    identifier = models.CharField(max_length=50)
    timeZone = models.CharField(max_length=50, default="America/Montevideo")
    mediaPath = models.CharField(max_length=100, default="/var/www/html/camera/")
    onDemandVideoDuration = models.IntegerField(default=15);

    @staticmethod
    def thisRaspi():
        try:
            return Raspi.objects.filter(address="127.0.0.1")[0]
        except IndexError:
            raise ValueError("no raspi found for address 127.0.0.1")

    def __str__(self):
        return self.identifier
    
class Relay(models.Model):
    name = models.CharField(max_length=50, unique=True)
    pin = models.IntegerField();
    isNormallyClosed = models.BooleanField(default=True)
    status = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.name

class Action(models.Model):
    raspi = models.ForeignKey(Raspi, on_delete=models.PROTECT)
    description = models.CharField(max_length=50, unique=True)
    relays = models.ManyToManyField(Relay)
    status = models.BooleanField(default=False, editable=False)
    
    def __redisKey(self, actionId):
        return "timed.action.{}".format(actionId)

    def __canExecute(self, priority):
        lastAction = ActionHistory.objects.filter(action_id=self.id).last()
        if lastAction:
            newStatus = not lastAction.status
            inconsistentStatus = len(self.relays.filter(status=newStatus)) > 0
            higherPriorityExists = lastAction.priority >= priority and r.get(self.__redisKey(lastAction.id)) is not None
            if inconsistentStatus:
                error = "action {} not executed due to a previous action with the same status".format(self.description)
            elif higherPriorityExists:
                error = "action {} not executed due to a previous action with higher priority".format(self.description)
            else:
                error = None
            canExecute = not inconsistentStatus and not higherPriorityExists
            return canExecute, newStatus, error;
        else:
            return True, True, None;

    def __setTurnOffTime(self, duration):
        key = self.__redisKey(self.id)
        r.sadd("timed.actions", key)
        r.set(key, self.id)
        r.expire(key, duration)
        logger.info("set automatic turn off for action {} after {} seconds".format(self.description, duration))

    def execute(self, priority, duration=0):
        if self.raspi.address == "127.0.0.1": 
            canExecute, status, error = self.__canExecute(priority)
            if canExecute:
                for r in self.relays.all():
                    toggleGPIO(not status if r.isNormallyClosed else status, r.pin)
                    r.status = status
                    r.save()
                self.status = status
                self.save()
                logger.info("action {} executed".format(self.description))
                if status and duration > 0:
                    self.__setTurnOffTime(duration)
                return status
            else:
                raise ValueError(error)
        else:
                # toggle remote relay
#                 url = 'http://{}{}'.format(relay.address, request.path)
#                 resp = requests.get(url, headers=request.headers, verify=False)
#                 if resp.status_code == 201:
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 else:
#                     return Response(resp.reason, status=resp.status_code)
            raise ValueError("action {} belongs to other raspi".format(self.description))

    def __str__(self):
        return self.description

class ActionHistory(models.Model):
    action = models.ForeignKey(Action, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True, editable=False)
    duration = models.IntegerField();
    priority = models.IntegerField(default=100);
    status = models.BooleanField(default=False, editable=False)
    
    class Meta:
        get_latest_by = 'date'

class Actionable(models.Model):
    action = models.ForeignKey(Action, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)
    priority = models.IntegerField();
        
    def __str__(self):
        return self.name
    
    def actuate(self, status):
        raise NotImplementedError
    
    class Meta:
        abstract=True
    
class Switch(Actionable):
    duration = models.IntegerField();
    pin = models.IntegerField();
    
    def actuate(self, status):
        if self.action:
            self.action.execute(status, self.priority, self.duration)
    
class Clock(Actionable):
    timeEnd = models.TimeField()
    timeStart = models.TimeField()

    def actuate(self, status):
        if self.action:
            # calculate duration
            timeZone = pytz.timezone(self.action.raspi.timezone)
            now = datetime.now(tz=timeZone)
            timeStart = timeZone.localize(datetime.combine(now, self.timeStart))
            timeEnd = timeZone.localize(datetime.combine(now, self.timeEnd)) if self.timeEnd > self.timeStart else timeZone.localize(datetime.combine(now + timedelta(days=1), self.timeEnd))
            timedelta = timeEnd - timeStart
            duration = timedelta.days * 24 * 3600 + timedelta.seconds
    
            self.action.execute(status, self.priority, duration)
                 
class LightSensor(Actionable):
    pin = models.IntegerField();
    threshold = models.IntegerField();

    def actuate(self, status):
        if self.action:
            self.action.execute(status, self.priority)
            
class PIRSensor(Actionable):
    durationLong = models.IntegerField();
    durationShort = models.IntegerField();
    longTimeEnd = models.TimeField()
    longTimeStart = models.TimeField()
    pin = models.IntegerField();

    def actuate(self, status):
        if self.action:
            # calculate duration
            timeZone = pytz.timezone(self.action.raspi.timezone)
            now = datetime.now(tz=timeZone)
            duration = self.durationLong if now >= self.longTimeStart and now < self.longTimeEnd else self.durationShort
            
            self.action.execute(status, self.priority, duration)

class Alarm(models.Model):
    armed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    detectPeople = models.BooleanField(default=False)
    fired = models.BooleanField(default=False)
    useCamera = models.BooleanField(default=False)
    
    class Meta:
        get_latest_by = 'date'
        
class Media(models.Model):
    dateCreated = models.DateTimeField('date created', auto_now_add=True)
    fileName = models.CharField(max_length=50)
    identifier = models.CharField(max_length=50)
    peopleDetected = models.BooleanField(default=False)
    triggeredByAlarm = models.BooleanField(default=False)
    type = models.CharField(max_length=5)
    
    def __redisKey(self):
        return "recording"
    
    def __canRecord(self):
        return r.get(self.__redisKey()) is None
    
    def __setRecordingFlag(self, duration):
        key = self.__redisKey()
        r.set(key, self.identifier)
        r.expire(key, duration)
        logger.info("set recording flag for {}, duration {} seconds".format(self.identifier, duration))

    @staticmethod
    def recordVideo():
        raspi = Raspi.thisRaspi()
        identifier = uuid.uuid1().hex
        fileNameH264 = "{}.h264".format(identifier)
        fileNameMP4 = "{}.mp4".format(identifier)
        
        media = Media()
        media.identifier = identifier
        media.type = "video"
        media.fileName = fileNameMP4
        
#         if media.__canRecord():          
#             with PiCamera() as camera:
#                 try:
#                     logger.info("start recording video {}".format(media.identifier))
#                     
#                     media.__setRecordingFlag(raspi.onDemandVideoDuration)
#                     
#                     camera.start_recording("{}{}".format(raspi.mediaPath, fileNameH264))
#                     camera.wait_recording(raspi.onDemandVideoDuration)
#                     camera.stop_recording()
#                     
#                     logger.info("stop recording video {} and release camera".format(media.identifier))
#                     # convert to mp4 format
#                     subprocess.run(["MP4Box", "-add", "{}{}".format(raspi.mediaPath, fileNameH264), "{}{}".format(raspi.mediaPath, fileNameMP4)], stdout=subprocess.DEVNULL)
#                     
#                     media.save()
#                     # remove H264 file
#                     os.remove("{}{}".format(raspi.mediaPath, fileNameH264))
#                 except PiCameraMMALError as error:
#                     logger.error(error)
#                 except:
#                     logger.error("Unexpected error:{}".format(sys.exc_info()[0]))
