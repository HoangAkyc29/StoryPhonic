from django.db import models
import uuid
from .novel import Novel

class ChunkContextMemory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    novel = models.ForeignKey(Novel, related_name='chunk_context_memories', on_delete=models.CASCADE, verbose_name='Novel')
    content = models.TextField(verbose_name='Context Content', help_text='Context memory text')
    index = models.PositiveIntegerField(db_index=True, help_text='Context memory order in novel')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('novel', 'index')
        ordering = ['index']
        verbose_name = 'Chunk Context Memory'
        verbose_name_plural = 'Chunk Context Memories'

    def __str__(self):
        return f"Context {self.index} of {self.novel.name}" 