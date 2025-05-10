from rest_framework import serializers
from ..models.chunk_context_memory import ChunkContextMemory

class ChunkContextMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChunkContextMemory
        fields = '__all__' 