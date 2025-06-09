from django.db import models
import uuid
from .novel import Novel
from .character import Character
from .chunk_annotation import ChunkAnnotation
from .voice import Voice

class SentenceAnnotation(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    novel = models.ForeignKey(Novel, related_name='sentence_annotations', on_delete=models.CASCADE, verbose_name='Novel')
    context = models.TextField(verbose_name='Context', help_text='Sentence context')
    index = models.PositiveIntegerField(db_index=True, help_text='Sentence order in novel')
    type = models.CharField(max_length=100, db_index=True, help_text='Type of annotation')
    raw_character = models.TextField(verbose_name='Raw Character', help_text='Raw character text')
    emotion = models.CharField(max_length=100, db_index=True, help_text='Emotion of the sentence')
    identity = models.ForeignKey(Character, related_name='sentence_annotations', on_delete=models.SET_NULL, null=True, verbose_name='Character')
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, db_index=True)
    voice_actor = models.CharField(max_length=100, blank=True, help_text='Voice actor (placeholder)')
    voice = models.ForeignKey(Voice, related_name='sentence_annotations', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Voice Actor')
    chunk_annotation_belong = models.ForeignKey(ChunkAnnotation, related_name='sentence_annotations', on_delete=models.SET_NULL, null=True, verbose_name='Chunk Annotation')
    chunk_index = models.PositiveIntegerField(help_text='Index of the chunk annotation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['index']
        verbose_name = 'Sentence Annotation'
        verbose_name_plural = 'Sentence Annotations'

    def __str__(self):
        return f"SentenceAnnotation {self.index} (Novel: {self.novel.name})" 