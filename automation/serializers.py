from rest_framework import serializers

from automation.models import Action, Alarm, Media, ActionHistory

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ('id', 'description', 'status')

class ActionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionHistory
        fields = ('action', 'date', 'priority', 'duration', 'status', 'who')

class GetActionHistorySerializer(serializers.ModelSerializer):
    action = ActionSerializer(many=False, read_only=True)
    class Meta:
        model = ActionHistory
        fields = ('id', 'action', 'date', 'priority', 'duration', 'status', 'who')

class AlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields = ('armed', 'fired', 'useCamera', 'detectPeople')
         
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('id', 'dateCreated', 'videoFile', 'thumbnail', 'classification', 'movementDetected')
