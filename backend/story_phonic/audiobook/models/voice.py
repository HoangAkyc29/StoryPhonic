from django.db import models
import uuid

class Voice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    voice_actor_name = models.CharField(max_length=100, unique=True, help_text='Name of the voice actor')
    s3_audio_data_url = models.URLField(help_text='URL to the voice actor audio data in S3')
    s3_voice_actor_metadata_url = models.URLField(help_text='URL to the voice actor metadata in S3')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Voice'
        verbose_name_plural = 'Voices'

    def __str__(self):
        return self.voice_actor_name 