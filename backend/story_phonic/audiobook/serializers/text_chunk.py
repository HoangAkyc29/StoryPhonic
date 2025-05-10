from rest_framework import serializers
from ..models.text_chunk import TextChunk

class TextChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextChunk
        fields = '__all__' 