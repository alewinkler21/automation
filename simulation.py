#!/usr/bin/env python

import os
import sys
import django
import pytz
from datetime import datetime, timedelta
import pandas as pd

import logger as logger
from logger import log

# setup django in order to use models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspberry.settings")
django.setup()
from automation.models import GPIOOutputDevice, GPIODeviceAction, GPIODeviceSimulation

def putInSlot(action):
    if action.dateOfUse.minute < 30:
        slot = '{}-{}'.format(str(action.dateOfUse.hour) + ":00", str(action.dateOfUse.hour) + ":30")
    else:
        slot = '{}-{}'.format(str(action.dateOfUse.hour) + ":30", str(action.dateOfUse.hour + 1) + ":00")
    return {"slot": slot, 
            "status": action.status, 
            "hour": action.dateOfUse.hour, 
            "minute": action.dateOfUse.minute, 
            "second": action.dateOfUse.second, 
            "deviceId": action.relay.id}
    
def calculateDayActions():
    timeZone = pytz.timezone("UTC")
    yesterday = (datetime.now(tz=timeZone) + timedelta(days=-1)).replace(hour=0, minute=0, second=0)
    thresholdStart = (yesterday + timedelta(days=-30)).replace(hour=0, minute=0, second=0)
    thresholdEnd = datetime.now(tz=timeZone).replace(hour=0, minute=0, second=0)
    
    djangoWeekDays = [2, 3, 4, 5, 6, 7, 1]
    
    getDayOfWeekActions = lambda status: GPIODeviceAction.objects.filter(
        dateOfUse__week_day=djangoWeekDays[yesterday.weekday()], status=status, dateOfUse__gte=thresholdStart, dateOfUse__lte=thresholdEnd)
        
    for st in [True, False]:
        actions = getDayOfWeekActions(st)
        if (len(actions) > 0):
            groupedActions = pd.DataFrame.from_dict(
                mapColor(putInSlot, actions)).sort_values(
                    ["hour", "minute", "second"],ascending=st).groupby(
                    ["deviceId", "slot", "hour"])
            
            for name, group in groupedActions:
                df = group.head(1)
                for index, row in df.iterrows():
                    try:
                        device = GPIOOutputDevice.objects.get(id=row.deviceId)
                        if device:
                            deviceSimulation = GPIODeviceSimulation()
                            deviceSimulation.day = yesterday
                            deviceSimulation.status = row.status
                            deviceSimulation.actionTime = yesterday.replace(hour=row.hour, minute=row.minute, second=row.second)
                            deviceSimulation.relay = device
                            deviceSimulation.save()
                    except GPIOOutputDevice.DoesNotExist:
                        logger.error("Fail saving device simulation:", sys.exc_info()[0])
        else:
            logger.warning("No actions found for range {} - {}".format(str(thresholdStart), str(thresholdEnd)))

calculateDayActions()

for a in GPIODeviceSimulation.objects.all():
    print(a)
