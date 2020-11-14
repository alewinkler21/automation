#!/usr/bin/env python3

import os
import django
import pytz
from django.utils import timezone
from datetime import datetime, timedelta

#setup django in order to use models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspberry.settings")
django.setup()
from automation.models import LightState

def deleteOldRecords():
    yesterday = datetime.now(tz=pytz.timezone("America/Montevideo")) - timedelta(days=1)
    LightState.objects.filter(date__lte = yesterday).delete()

deleteOldRecords()