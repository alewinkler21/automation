from django.core.management.base import BaseCommand, CommandError
from automation.models import Action, Switch, Clock, Relay, LightSensor, PIRSensor
from automation import gpio

import signal
import sys
import time
import logger
from threading import Thread
import redis

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

class ActionsTimer(Thread):
    
    def __getAction(self, actionId):
        try:
            return Action.objects.get(id=actionId)
        except Action.DoesNotExist:
            return  None

    def run(self):
        keysList = "timed.actions"
        while True:
            logger.debug("Let's check what to turn off")
            
            timedActionsKeys = r.smembers(keysList)
            if len(timedActionsKeys) > 0:
                for ta in timedActionsKeys:
                    timedActionKey = str(ta, "UTF-8")
                    actionId = r.get(timedActionKey)
                    if actionId is None:
                        actionId = timedActionKey.split(".")[-1]
                        action = self.__getAction(actionId)
                        if action:
                            try:
                                action.execute(status=False)
                                
                                logger.debug("action {} expired".format(action))
                            except ValueError as e:
                                r.srem(keysList, timedActionKey)
                                logger.warning(e)
                        else:
                            r.delete(timedActionKey)
                            r.srem(keysList, timedActionKey)
                            logger.error("action {} doesn't exist".format(actionId))
                    else:
                        action = self.__getAction(str(actionId, "UTF-8"))
                        if action:
                            secondsRemaining = r.ttl(timedActionKey)
                            logger.debug("{} seconds left to turn off {}".format(secondsRemaining, action))
            else:
                logger.debug("No valid timed actions")
            time.sleep(2)

class ClockTimer(Thread):
    
    def __init__(self, clock):
        super(ClockTimer, self).__init__()
        self.clock = clock
        
    def run(self):
        while True:
            logger.debug("Clock {} tick".format(self.clock))
            
            self.clock.actuate()
            time.sleep(2)

class LightSensorMonitor(Thread):

    def __init__(self, sensor):
        super(LightSensorMonitor, self).__init__()
        self.sensor = sensor

    def run(self):
        while True:
            darkness = gpio.timeToHigh(self.sensor)
            self.sensor.setDarkness(darkness)
            time.sleep(1)

class PIRSensorMonitor(Thread):

    def __init__(self, sensor):
        super(PIRSensorMonitor, self).__init__()
        self.sensor = sensor

    def run(self):
        gpio.initSensor(self.sensor)
        previousState = False
        while True:
            movement = gpio.readSensorValue(self.sensor)
            if movement:
                if movement != previousState:  # avoid repeating the same signal
                    self.sensor.actuate()
                else:
                    logger.debug("Movement ignored")
            else:
                logger.debug("No movement")
            previousState = movement
            time.sleep(1)

def initRelays():
    for r in Relay.objects.filter(isNormallyClosed=True):
        gpio.toggle(True, r.pin)
    logger.info("Relays initiated")

def buttonPressed(button):
    button.actuate()

def initButtons():
    for button in Switch.objects.all():
        gpio.initButton(button, buttonPressed)
    logger.info("Buttons initiated")
        
def initClocks():
    for clock in Clock.objects.all():
        clockTimer = ClockTimer(clock)
        clockTimer.setDaemon(True)
        clockTimer.start()
    logger.info("Clocks initiated")

def initLightSensors():
    for lightSensor in LightSensor.objects.all():
        lightSensorMonitor = LightSensorMonitor(lightSensor)
        lightSensorMonitor.setDaemon(True)
        lightSensorMonitor.start()
    logger.info("Light sensors initiated")

def initPIRSensors():
    for pirSensor in PIRSensor.objects.all():
        pirSensorMonitor = PIRSensorMonitor(pirSensor)
        pirSensorMonitor.setDaemon(True)
        pirSensorMonitor.start()
    logger.info("PIR sensors initiated")

def startActionsTimer():
    actionsTimer = ActionsTimer()
    actionsTimer.setDaemon(True)
    actionsTimer.start()
    logger.info("Actions timer initiated")
    actionsTimer.join()

def terminateProcess(signalNumber, frame):
    logger.info("(SIGTERM) terminating the process")
    gpio.cleanUp()
    sys.exit()

class Command(BaseCommand):
    help = "Start automation daemons"

    def add_arguments(self, parser):
        pass
                    
    def handle(self, *args, **options):
        signal.signal(signal.SIGTERM, terminateProcess)
        try:
            initRelays()
            initButtons()
            initClocks()
            initLightSensors()
            initPIRSensors()
            startActionsTimer()
        except KeyboardInterrupt:
            gpio.cleanUp()
            sys.exit()
