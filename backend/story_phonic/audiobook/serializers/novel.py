from rest_framework import serializers
from ..models.novel import Novel
from django.core.validators import FileExtensionValidator

class NovelSerializer(serializers.ModelSerializer):
    content_file = serializers.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'docx'])],
        help_text="Upload PDF, TXT or DOCX file"
    )
    
    class Meta:
        model = Novel
        fields = ['id', 'user', 'name', 'content', 'content_file', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        
    def validate(self, data):
        if not data.get('content') and not data.get('content_file'):
            raise serializers.ValidationError("Either content or content_file must be provided")
        return data 