from django.db import models
import uuid
from oauth.models.user import User

class Novel(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name='novels', on_delete=models.CASCADE, verbose_name='Owner')
    name = models.CharField(max_length=255, db_index=True, verbose_name='Novel Name', help_text='Name of the novel')
    content = models.TextField(verbose_name='Content', help_text='Full content of the novel')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    s3_audio_metadata_url = models.URLField(max_length=500, null=True, blank=True, verbose_name='S3 Audio Metadata URL')
    s3_audio_file_url = models.URLField(max_length=500, null=True, blank=True, verbose_name='S3 Audio File URL')

    class Meta:
        verbose_name = 'Novel'
        verbose_name_plural = 'Novels'
        ordering = ['-created_at']

    def __str__(self):
        return self.name 