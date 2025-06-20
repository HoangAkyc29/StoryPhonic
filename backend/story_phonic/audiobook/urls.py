from rest_framework.routers import DefaultRouter
from .views.novel import NovelViewSet
from .views.text_chunk import TextChunkViewSet
from .views.chunk_context_memory import ChunkContextMemoryViewSet
from .views.chunk_annotation import ChunkAnnotationViewSet
from .views.character import CharacterViewSet
from .views.sentence_annotation import SentenceAnnotationViewSet
from .views.audio_views import upload_audio_to_s3_view
from .views.voice import VoiceViewSet
from django.urls import path

router = DefaultRouter()
router.register(r'novels', NovelViewSet, basename='novel')
router.register(r'text-chunks', TextChunkViewSet, basename='text-chunk')
router.register(r'chunk-context-memories', ChunkContextMemoryViewSet, basename='chunk-context-memory')
router.register(r'chunk-annotations', ChunkAnnotationViewSet, basename='chunk-annotation')
router.register(r'characters', CharacterViewSet, basename='character')
router.register(r'sentence-annotations', SentenceAnnotationViewSet, basename='sentence-annotation')
router.register(r'voices', VoiceViewSet, basename='voice')

urlpatterns = router.urls + [
    path('upload-audio-to-s3/', upload_audio_to_s3_view, name='upload-audio-to-s3'),
] 