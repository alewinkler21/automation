from django.core.management.base import BaseCommand, CommandError
from automation.models import Relay, Action, ActionHistory, Switch, Clock, LightSensor, PIRSensor
from datetime import time
from raspberry.settings import AUTOMATION

class Command(BaseCommand):
    help = "Add default data to database"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        ActionHistory.objects.all().delete()
        LightSensor.objects.all().delete()
        PIRSensor.objects.all().delete()
        Switch.objects.all().delete()
        Clock.objects.all().delete()
        Action.objects.all().delete()
        Relay.objects.all().delete()
        
        self.stdout.write("Existent data was deleted")
        
        relay1 = Relay()
        relay1.name = "Module1"
        relay1.pin = 23
        relay1.isNormallyClosed = True
        relay1.save()

        self.stdout.write("Relay {} was created".format(relay1))
    
        relay2 = Relay()
        relay2.name = "Module2"
        relay2.pin = 24
        relay2.isNormallyClosed = True
        relay2.save()
        
        self.stdout.write("Relay {} was created".format(relay2))
        
        action1 = Action()
        action1.address = AUTOMATION["address"]
        action1.description = "Lámpara Mesita"
        action1.save()
        action1.relays.add(relay1)

        self.stdout.write("Action {} was created".format(action1))

        action2 = Action()
        action2.address = AUTOMATION["address"]
        action2.description = "Luz Techo"
        action2.save()
        action2.relays.add(relay2)
        
        self.stdout.write("Action {} was created".format(action2))
        
        action3 = Action()
        action3.address = AUTOMATION["address"]
        action3.description = "Lámpara Mesita y Luz Techo"
        action3.save()
        action3.relays.add(relay1)
        action3.relays.add(relay2)
        
        self.stdout.write("Action {} was created".format(action3))
        
        switch = Switch()
        switch.name = "Interruptor Puerta"
        switch.pin = 16
        switch.duration = 30
        switch.priority = 1
        switch.action = action2
        switch.save()
        
        self.stdout.write("Switch {} was created".format(switch))
        
        clock = Clock()
        clock.name = "10 a 12"
        clock.priority = 3
        clock.timeStart = time(hour = 10, minute = 0)
        clock.timeEnd = time(hour = 12, minute = 0)
        clock.action = action1
        clock.save()
        
        self.stdout.write("Clock {} was created".format(clock))
        
        lightSensor = LightSensor()
        lightSensor.name = "Sensor Luz"
        lightSensor.priority = 3
        lightSensor.pin = 23
        lightSensor.threshold = 10
        lightSensor.action = action1
        lightSensor.save()
        
        self.stdout.write("LightSensor {} was created".format(lightSensor))
        
        pirSensor = PIRSensor()
        pirSensor.name = "Sensor Movimiento"
        pirSensor.priority = 2
        pirSensor.pin = 24
        pirSensor.durationLong = 3600
        pirSensor.durationShort = 30
        pirSensor.longTimeStart = time(hour = 18, minute = 30)
        pirSensor.longTimeEnd = time(hour = 23, minute = 59)
        pirSensor.action = action3
        pirSensor.save()
        
        self.stdout.write("PIRSensor {} was created".format(pirSensor))
                
        self.stdout.write(self.style.SUCCESS("Initial data was created successfully"))
