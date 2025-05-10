from django.db import models
import uuid
from .novel import Novel

class Character(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    novel = models.ForeignKey(Novel, related_name='characters', on_delete=models.CASCADE, verbose_name='Novel')
    name = models.CharField(max_length=255, help_text='Character name')
    character_info = models.TextField(verbose_name='Character Info', help_text='Information about the character')
    index = models.PositiveIntegerField(db_index=True, help_text='Character order in novel')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['index']
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'

    def __str__(self):
        return f"{self.name} (Novel: {self.novel.name})" 