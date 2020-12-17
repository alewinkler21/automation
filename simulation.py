#!/usr/bin/env python3

import sys
import RPi.GPIO as GPIO
import time
import os
import django
import pytz
from django.utils import timezone
from datetime import datetime, timedelta
import logger as logger
import redis
import signal

# setup django in order to use models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspberry.settings")
django.setup()
from automation.models import Relay, RelayAction

timeZone = pytz.timezone("America/Montevideo")
sharedMemory = redis.Redis(host='127.0.0.1', port=6379, db=0)

def saveDeviceAction(device, status, tmstmp):
    action = RelayAction()
    action.dateOfUse = tmstmp
    action.status = status
    action.isAutomatic = True
    action.relay = device
    action.save()
    # set device status
    device.status = status
    device.save()

def main():
    while True:
        devices = Relay.objects.filter(enabled=True, autoEnabled=True, address='127.0.0.1', status=False)
        now = datetime.now(tz=timeZone)
        for d in devices:
            longTimeStart = timeZone.localize(datetime.combine(now, d.longTimeStart))
            longTimeEnd = timeZone.localize(datetime.combine(now, d.longTimeEnd)) if d.longTimeEnd > d.longTimeStart else timeZone.localize(datetime.combine(now + timedelta(days=1), d.longTimeEnd))
            if now >= longTimeStart and now < longTimeEnd:
                turnOffDatetime = longTimeEnd
                # turn on device
                GPIO.setup(d.pinNumber, GPIO.OUT)
                GPIO.output(d.pinNumber, GPIO.HIGH)
                # save event
                saveDeviceAction(d, True, now)
                # set automatic turn off
                if sharedMemory.set(d.address + '-' + str(d.id), str(turnOffDatetime)):
                    logger.info("Set automatic turn off for device: {} longTimeStart: {} longTimeEnd: {} Off: {}".format(d.name,  
                                                                                                                          longTimeStart.strftime("%Y-%m-%d %H:%M:%S"), 
                                                                                                                          longTimeEnd.strftime("%Y-%m-%d %H:%M:%S"),
                                                                                                                          turnOffDatetime.strftime("%Y-%m-%d %H:%M:%S")))
                else:
                    logger.error("Set automatic turn off failed for device {}".format(d.name))
    time.sleep(30)

def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    GPIO.cleanup()
    sys.exit()

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminateProcess)
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

