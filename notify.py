# import requests
import json
import os
import django
from datetime import datetime
import logger as logger

#setup django in order to use models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspberry.settings")
django.setup()
from automation.models import NotificationClient

gcm_url = "https://android.googleapis.com/gcm/send"
gcm_api_key = "AIzaSyAGmzAgXvGMnsF63gihg1EUMSu_kQSXsNs"
     
def notify(message):
    result = False
    for nc in NotificationClient.objects.all():
        data = '{"registration_ids":["' + nc.registration_id + '"],"data":{"message":"%s"}}' % message
        headers = {'Authorization': 'key=' + gcm_api_key, 'Content-Type': 'application/json'}
        request = requests.post(url = gcm_url, data = data, headers = headers)
        if request.status_code == 200:
            obj = json.loads(request.text)
            if not obj is None:
                error = obj["results"][0].get("error")
            else:
                error = "obj is None"
            if error is None:
                logger.debug('Result: {} {}'.format("Notification sent", nc.device_id))
                result = True
            else:
                logger.debug('Result: {}'.format(str(obj["results"][0].get("error"))))
    return result