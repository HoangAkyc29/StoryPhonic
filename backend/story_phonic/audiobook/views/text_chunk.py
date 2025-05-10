from rest_framework import viewsets, permissions
from ..models.text_chunk import TextChunk
from ..serializers.text_chunk import TextChunkSerializer
from ..permissions import IsOwnerOrAdmin

class TextChunkViewSet(viewsets.ModelViewSet):
    serializer_class = TextChunkSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = TextChunk.objects.filter(is_deleted=False, novel__is_deleted=False)
        if hasattr(user, 'roles') and user.roles.filter(name='admin').exists():
            return qs
        return qs.filter(novel__user=user) 