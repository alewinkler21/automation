from rest_framework import serializers

from automation.models import Action, Alarm, Media, ActionHistory

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ('id', 'description', 'status')

class ActionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionHistory
        fields = ('action', 'date', 'priority', 'duration', 'status')

class AlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields = ('armed', 'fired', 'useCamera', 'detectPeople')
         
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('id', 'dateCreated', 'videoFile', 'thumbnail', 'classification', 'movementDetected')
