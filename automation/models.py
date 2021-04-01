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
from raspberry.settings import TIME_ZONE, AUTOMATION
#from picamera import PiCamera, PiCameraMMALError

r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    
class Relay(models.Model):
    name = models.CharField(max_length=50, unique=True)
    pin = models.IntegerField();
    isNormallyClosed = models.BooleanField(default=True)
    status = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.name

class Action(models.Model):
    address = models.CharField(max_length=50, default="127.0.0.1")
    description = models.CharField(max_length=50, unique=True)
    relays = models.ManyToManyField(Relay)
    status = models.BooleanField(default=False, editable=False)
    
    def turnOffFlag(self):
        return "on.action.{}".format(self.id)

    def keepOffFlag(self):
        return "off.action.{}".format(self.id)

    def __canExecute(self, priority, status):
        relatedActions = Action.objects.filter(relays__id__in = self.relays.all()).distinct()
        lastActionExecuted = ActionHistory.objects.filter(action__id__in = relatedActions).last()
        if status is None:
            status = not self.status
        higherPriorityExists = (status 
                                and lastActionExecuted is not None 
                                and lastActionExecuted.priority > priority 
                                and (r.get(lastActionExecuted.action.turnOffFlag()) is not None
                                     or r.get(lastActionExecuted.action.keepOffFlag()) is not None))
        inconsistentStatus = (lastActionExecuted is not None 
                              and lastActionExecuted.action != self 
                              and len(self.relays.filter(status=status)) > 0)
        if inconsistentStatus:
            error = "action {} not executed due to an inconsistent status".format(self.description)
        elif higherPriorityExists:
            error = "action {} not executed due to a previous action with higher priority".format(self.description)
        else:
            error = None
        canExecute = not inconsistentStatus and not higherPriorityExists
        
        return canExecute, status, error

    def __setActionTimer(self, duration):
        key = self.turnOffFlag()
        r.sadd("timed.actions", key)
        r.set(key, self.id)
        r.expire(key, duration)
        logger.info("set automatic turn off for action {} after {} seconds".format(self.description, duration))

    def __removeActionTimer(self):
        key = self.turnOffFlag()
        r.srem("timed.actions", key)
        r.delete(key)
        logger.info("remove automatic turn off for action {}".format(self.description))

    def __setKeepOffFlag(self, duration):
        key = self.keepOffFlag()
        r.set(key, self.id)
        r.expire(key, duration)
        logger.info("set keep off for action {} during {} seconds".format(self.description, duration))

    def execute(self, priority = 0, status = None, duration=0):
        if self.address == "127.0.0.1": 
            canExecute, status, error = self.__canExecute(priority, status)
            if canExecute:
                for r in self.relays.all():
                    toggleGPIO(not status if r.isNormallyClosed else status, r.pin)
                    r.status = status
                    r.save()
                self.status = status
                self.save()
                # save history
                actionHistory = ActionHistory()
                actionHistory.action = self
                actionHistory.priority = priority
                actionHistory.status = status
                actionHistory.duration = duration
                actionHistory.save()
                
                logger.info("action {} executed".format(self.description))
                if not status:
                    self.__removeActionTimer()
                if duration > 0:
                    self.__setActionTimer(duration) if status else self.__setKeepOffFlag(duration)

                return status, priority, duration
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
    
    def actuate(self):
        raise NotImplementedError
    
    class Meta:
        abstract=True
    
class Switch(Actionable):
    duration = models.IntegerField();
    pin = models.IntegerField();
    
    def actuate(self):
        if self.action:
            self.action.execute(priority=self.priority, duration=self.duration)
    
class Clock(Actionable):
    timeEnd = models.TimeField()
    timeStart = models.TimeField()

    def actuate(self):
        if self.action:
            # calculate duration
            timeZone = pytz.timezone(TIME_ZONE)
            now = datetime.now(tz=timeZone)
            timeStart = timeZone.localize(datetime.combine(now, self.timeStart))
            timeEnd = timeZone.localize(datetime.combine(now, self.timeEnd)) if self.timeEnd > self.timeStart else timeZone.localize(datetime.combine(now + timedelta(days=1), self.timeEnd))
            timedelta = timeEnd - now
            duration = timedelta.days * 24 * 3600 + timedelta.seconds
            # calculate status
            status = True if now >= timeStart and now < timeEnd else False
            if self.action.status != status:     
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
            timeZone = pytz.timezone(TIME_ZONE)
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
    
    def turnOffFlag(self):
        return "recording"
    
    def __canRecord(self):
        return r.get(self.turnOffFlag()) is None
    
    def __setRecordingFlag(self, duration):
        key = self.turnOffFlag()
        r.set(key, self.identifier)
        r.expire(key, duration)
        logger.info("set recording flag for {}, duration {} seconds".format(self.identifier, duration))

    @staticmethod
    def recordVideo():
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
#                     media.__setRecordingFlag(AUTOMATION["onDemandVideoDuration"])
#                     
#                     camera.start_recording("{}{}".format(AUTOMATION["mediaPath"], fileNameH264))
#                     camera.wait_recording(AUTOMATION["onDemandVideoDuration"])
#                     camera.stop_recording()
#                     
#                     logger.info("stop recording video {} and release camera".format(media.identifier))
#                     # convert to mp4 format
#                     subprocess.run(["MP4Box", "-add", "{}{}".format(AUTOMATION["mediaPath"], fileNameH264), "{}{}".format(AUTOMATION["mediaPath"], fileNameMP4)], stdout=subprocess.DEVNULL)
#                     
#                     media.save()
#                     # remove H264 file
#                     os.remove("{}{}".format(AUTOMATION["mediaPath"], fileNameH264))
#                 except PiCameraMMALError as error:
#                     logger.error(error)
#                 except:
#                     logger.error("Unexpected error:{}".format(sys.exc_info()[0]))
