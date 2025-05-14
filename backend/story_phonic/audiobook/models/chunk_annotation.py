from django.db import models
import uuid
from .novel import Novel

class ChunkAnnotation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    novel = models.ForeignKey(Novel, related_name='chunk_annotations', on_delete=models.CASCADE, verbose_name='Novel')
    raw_text = models.TextField(verbose_name='Raw Text', help_text='Original text before cleaning')
    clean_text = models.TextField(verbose_name='Clean Text', help_text='Cleaned text')
    index = models.PositiveIntegerField(db_index=True, help_text='Annotation order in novel')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='completed', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('novel', 'index')
        ordering = ['index']
        verbose_name = 'Chunk Annotation'
        verbose_name_plural = 'Chunk Annotations'

    def __str__(self):
        return f"Annotation {self.index} of {self.novel.name}" 