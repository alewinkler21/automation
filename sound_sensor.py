#!/usr/bin/env python3

import sys
import RPi.GPIO as GPIO
import time
import os
import django
import pytz
from datetime import datetime
import logger as logger

# setup django in order to use models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspberry.settings")
django.setup()
from automation.models import LightState, GPIOOutputDevice, GPIODeviceAction, Alarm

pinsSensors = [26]
timeZone = pytz.timezone("America/Montevideo")
lastSoundTime = None
accumulatedIntervals = 0

def saveDeviceAction(device, status, tmstmp):
    action = GPIODeviceAction()
    action.dateOfUse = tmstmp
    action.status = status
    action.isAutomatic = False
    action.relay = device
    action.save()
    # set device status
    device.status = status
    device.save()

def soundDetected(pin):
  global lastSoundTime, accumulatedIntervals
  now = datetime.now(tz=timeZone)
  interval = (now - lastSoundTime).total_seconds() if lastSoundTime else 0.0
  lastSoundTime = now
  if interval < 1:
    accumulatedIntervals += interval
    if accumulatedIntervals >= 0.25 and accumulatedIntervals < 0.65:
      interval = 0
      accumulatedIntervals = 0
      logger.debug("clap detected")
      time.sleep(1)
      devices = GPIOOutputDevice.objects.filter(clapEnabled=True)
      for d in devices:
        GPIO.setup(d.pinNumber, GPIO.OUT)
        GPIO.output(d.pinNumber, (not d.status))
        logger.debug("Set status " + str((not d.status)) + " for pin " + str(d.pinNumber))
        saveDeviceAction(d, (not d.status), now)
  else:
    accumulatedIntervals = 0

def initSensors():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  for p in pinsSensors:
    # set the pin as output and value to off 
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, GPIO.LOW)
    time.sleep(0.1)
    # change the pin back to input and set callback for rising event
    GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(p, GPIO.RISING, callback = soundDetected)

def main():
#  time.sleep(30)
  
  initSensors()
  
  while True:
    time.sleep(1)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()
