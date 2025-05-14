from rest_framework import serializers
from ..models.novel import Novel
from django.core.validators import FileExtensionValidator

class NovelSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False, allow_blank=True)
    content_file = serializers.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'docx'])],
        help_text="Upload PDF, TXT or DOCX file"
    )
    
    class Meta:
        model = Novel
        fields = [
            'id', 'user', 'name', 'content', 'content_file', 
            'status', 'created_at', 's3_audio_metadata_url', 's3_audio_file_url'
        ]
        read_only_fields = ['id', 'user', 'created_at', 's3_audio_metadata_url', 's3_audio_file_url']
        
    def validate(self, data):
        if not data.get('content') and not data.get('content_file'):
            raise serializers.ValidationError("Either content or content_file must be provided")
        return data 

    def create(self, validated_data):
        validated_data.pop('content_file', None)
        return super().create(validated_data) 