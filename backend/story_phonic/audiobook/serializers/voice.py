from rest_framework import serializers
from ..models.voice import Voice

class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__' 