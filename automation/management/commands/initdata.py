from django.core.management.base import BaseCommand, CommandError
from automation.models import Relay, Action, ActionHistory, Switch, Clock
from datetime import time
from raspberry.settings import AUTOMATION

class Command(BaseCommand):
    help = "Add default data to database"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        ActionHistory.objects.all().delete()
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

        self.stdout.write("Relay {} was created".format(relay1.name))
    
        relay2 = Relay()
        relay2.name = "Module2"
        relay2.pin = 24
        relay2.isNormallyClosed = True
        relay2.save()
        
        self.stdout.write("Relay {} was created".format(relay2.name))
        
        action1 = Action()
        action1.address = AUTOMATION["address"]
        action1.description = "Lámpara Mesita"
        action1.save()
        action1.relays.add(relay1)

        self.stdout.write("Action {} was created".format(action1.description))

        action2 = Action()
        action2.address = AUTOMATION["address"]
        action2.description = "Luz Techo"
        action2.save()
        action2.relays.add(relay2)
        
        self.stdout.write("Action {} was created".format(action2.description))
        
        action3 = Action()
        action3.address = AUTOMATION["address"]
        action3.description = "Lámpara Mesita y Luz Techo"
        action3.save()
        action3.relays.add(relay1)
        action3.relays.add(relay2)
        
        self.stdout.write("Action {} was created".format(action3.description))
        
        switch = Switch()
        switch.name = "Interruptor Puerta"
        switch.pin = 16
        switch.duration = 30
        switch.priority = 1
        switch.action = action2
        switch.save()
        
        self.stdout.write("Switch {} was created".format(switch.name))
        
        clock = Clock()
        clock.name = "10 a 12"
        clock.priority = 3
        clock.timeStart = time(hour = 10, minute = 0)
        clock.timeEnd = time(hour = 12, minute = 0)
        clock.action = action3
        clock.save()
        
        self.stdout.write("Clock {} was created".format(clock.name))
                
        self.stdout.write(self.style.SUCCESS("Initial data was created successfully"))
