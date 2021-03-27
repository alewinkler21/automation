from django.core.management.base import BaseCommand, CommandError
from automation.models import Raspi, Relay, Action, ActionHistory

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
        while True:
            logger.debug("Let's check what to turn off")
            
            timedActionsKeys = r.smembers("timed.actions")
            if len(timedActionsKeys) > 0:
                for ta in timedActionsKeys:
                    timedActionKey = str(ta, "UTF-8")
                    actionId = r.get(timedActionKey)
                    if actionId is None:
                        actionId = timedActionKey.split(".")[-1]
                        action = self.__getAction(actionId)
                        newStatus, priority, duration = action.execute(status=False)
                        
                        actionHistory = ActionHistory()
                        actionHistory.action = action
                        actionHistory.priority = priority
                        actionHistory.status = newStatus
                        actionHistory.duration = duration
                        actionHistory.save()
                        
                        r.srem("timed.actions", timedActionKey)
                        
                        logger.debug("action {} expired".format(timedActionKey))
                    else:
                        action = self.__getAction(str(actionId, "UTF-8"))
                        if action:
                            secondsRemaining = r.ttl(timedActionKey)
                            logger.debug("{} seconds left to turn off {}".format(secondsRemaining, action))
            else:
                logger.debug("No valid timed actions")
                    
#             devices = Relay.objects.filter(enabled=True, autoEnabled=True, address='127.0.0.1', status=True)
#             now = datetime.now(tz=timeZone)
#             for d in devices:
#                 turnOffSavedDatetime = sharedMemory.get(d.address + '-' + str(d.id))
#                 if turnOffSavedDatetime:
#                     turnOffDatetime = parseDate(str(turnOffSavedDatetime, 'UTF-8'))
#                     if now >= turnOffDatetime:
#                         logger.info("Turning off and removing automated device: " + str(d))
#                         GPIO.setup(d.pinNumber, GPIO.OUT)
#                         GPIO.output(d.pinNumber, GPIO.LOW)
#                         saveDeviceAction(d, False, now)
#                         # remove automated device
#                         sharedMemory.delete(d.address + '-' + str(d.id))
#                 else:
#                     logger.debug("Automated device is not in shared memory:" + str(d))
            time.sleep(2)

class Command(BaseCommand):
    help = "Start automation daemons"

    def add_arguments(self, parser):
        pass

    def terminateProcess(self, signalNumber, frame):
        self.stdout.write("(SIGTERM) terminating the process")
        #GPIO.cleanup()
        sys.exit()
    
    def handle(self, *args, **options):
        signal.signal(signal.SIGTERM, self.terminateProcess)
        try:
            actionsTimer = ActionsTimer()
            actionsTimer.setDaemon(True)
            actionsTimer.start()
            
            actionsTimer.join()
        except KeyboardInterrupt:
            #GPIO.cleanup()
            sys.exit()