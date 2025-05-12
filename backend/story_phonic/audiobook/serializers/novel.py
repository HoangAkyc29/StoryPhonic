from rest_framework import serializers
from ..models.novel import Novel

class NovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        fields = ['id', 'user', 'name', 'content', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'created_at'] 