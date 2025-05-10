from rest_framework import serializers
from ..models.sentence_annotation import SentenceAnnotation

class SentenceAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentenceAnnotation
        fields = '__all__' 