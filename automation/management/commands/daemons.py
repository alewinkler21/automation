from django.core.management.base import BaseCommand, CommandError
from automation.models import Action, ActionHistory, Switch
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
                                status, priority, duration = action.execute(status=False)

                                actionHistory = ActionHistory()
                                actionHistory.action = action
                                actionHistory.priority = priority
                                actionHistory.status = status
                                actionHistory.duration = duration
                                actionHistory.save()
                                
                                r.srem(keysList, timedActionKey)
                                
                                logger.debug("action {} expired".format(timedActionKey))
                            except ValueError as e:
                                r.srem(keysList, timedActionKey)
                                logger.error(e)
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

class Command(BaseCommand):
    help = "Start automation daemons"

    def add_arguments(self, parser):
        pass

    def terminateProcess(self, signalNumber, frame):
        self.stdout.write("(SIGTERM) terminating the process")
        #GPIO.cleanup()
        sys.exit()
    
    def buttonPressed(self, button):
        print("Button {} was pushed!".format(button.name))
        #button.actuate()
    
    def initButtons(self):
        for button in Switch.objects.all():
            gpio.initButton(button, self.buttonPressed)
            
    def startActionsTimer(self):
        actionsTimer = ActionsTimer()
        actionsTimer.setDaemon(True)
        actionsTimer.start()
        actionsTimer.join()
                    
    def handle(self, *args, **options):
        signal.signal(signal.SIGTERM, self.terminateProcess)
        try:
            self.initButtons()
            self.startActionsTimer()
        except KeyboardInterrupt:
            #GPIO.cleanup()
            sys.exit()
