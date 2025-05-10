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
router.register(r'novels', NovelViewSet)
router.register(r'text-chunks', TextChunkViewSet)
router.register(r'chunk-context-memories', ChunkContextMemoryViewSet)
router.register(r'chunk-annotations', ChunkAnnotationViewSet)
router.register(r'characters', CharacterViewSet)
router.register(r'sentence-annotations', SentenceAnnotationViewSet)

urlpatterns = router.urls 