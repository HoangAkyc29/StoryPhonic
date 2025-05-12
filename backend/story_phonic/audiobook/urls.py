from rest_framework.routers import DefaultRouter
from .views import (
    NovelViewSet,
    TextChunkViewSet,
    ChunkContextMemoryViewSet,
    ChunkAnnotationViewSet,
    CharacterViewSet,
    SentenceAnnotationViewSet,
)

router = DefaultRouter()
router.register(r'novels', NovelViewSet, basename='novel')
router.register(r'text-chunks', TextChunkViewSet, basename='text-chunk')
router.register(r'chunk-context-memories', ChunkContextMemoryViewSet, basename='chunk-context-memory')
router.register(r'chunk-annotations', ChunkAnnotationViewSet, basename='chunk-annotation')
router.register(r'characters', CharacterViewSet, basename='character')
router.register(r'sentence-annotations', SentenceAnnotationViewSet, basename='sentence-annotation')

urlpatterns = router.urls 