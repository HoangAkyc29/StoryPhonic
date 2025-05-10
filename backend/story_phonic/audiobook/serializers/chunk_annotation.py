from rest_framework import serializers
from ..models.chunk_annotation import ChunkAnnotation

class ChunkAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChunkAnnotation
        fields = '__all__' 