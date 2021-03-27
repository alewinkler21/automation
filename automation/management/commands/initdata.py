from django.core.management.base import BaseCommand, CommandError
from automation.models import Raspi, Relay, Action, ActionHistory

import socket

class Command(BaseCommand):
    help = "Add default data to database"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        ActionHistory.objects.all().delete()
        Action.objects.all().delete()
        Raspi.objects.all().delete()
        Relay.objects.all().delete()
        
        self.stdout.write("Existent data was deleted")
        
        raspi = Raspi()
        raspi.identifier = socket.gethostname()
        raspi.save()
        
        self.stdout.write("Raspi was created")
        
        relay1 = Relay()
        relay1.name = "Module1"
        relay1.pin = 23
        relay1.isNormallyClosed = True
        relay1.save()

        self.stdout.write("Relay1 data was created")
    
        relay2 = Relay()
        relay2.name = "Module2"
        relay2.pin = 24
        relay2.isNormallyClosed = True
        relay2.save()
        
        self.stdout.write("Relay2 data was created")
        
        action1 = Action()
        action1.raspi = raspi
        action1.description = "Module 1"
        action1.save()
        action1.relays.add(relay1)

        self.stdout.write("Action1 data was created")

        action2 = Action()
        action2.raspi = raspi
        action2.description = "Module 2"
        action2.save()
        action2.relays.add(relay2)
        
        self.stdout.write("Action2 data was created")
        
        self.stdout.write(self.style.SUCCESS("Initial data was created successfully"))
