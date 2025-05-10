from django.db import models
import uuid
from .novel import Novel

class TextChunk(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    novel = models.ForeignKey(Novel, related_name='text_chunks', on_delete=models.CASCADE, verbose_name='Novel')
    content = models.TextField(verbose_name='Chunk Content', help_text='Text content of the chunk')
    index = models.PositiveIntegerField(db_index=True, help_text='Chunk order in novel')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('novel', 'index')
        ordering = ['index']
        verbose_name = 'Text Chunk'
        verbose_name_plural = 'Text Chunks'

    def __str__(self):
        return f"Chunk {self.index} of {self.novel.name}" 