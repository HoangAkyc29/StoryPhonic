from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models.novel import Novel
from ..serializers.novel import NovelSerializer
from ..permissions import IsOwnerOrAdmin

class NovelViewSet(viewsets.ModelViewSet):
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Novel.objects.filter(is_deleted=False)
        if hasattr(user, 'roles') and user.roles.filter(name='admin').exists():
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete novel và toàn bộ object con
        instance.is_deleted = True
        instance.save()
        # Soft delete các object con
        for rel in ['text_chunks', 'chunk_context_memories', 'chunk_annotations', 'characters', 'sentence_annotations']:
            for obj in getattr(instance, rel).all():
                obj.is_deleted = True
                obj.save() 