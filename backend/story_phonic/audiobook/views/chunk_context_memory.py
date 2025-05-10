from rest_framework import viewsets, permissions
from ..models.chunk_context_memory import ChunkContextMemory
from ..serializers.chunk_context_memory import ChunkContextMemorySerializer
from ..permissions import IsOwnerOrAdmin

class ChunkContextMemoryViewSet(viewsets.ModelViewSet):
    serializer_class = ChunkContextMemorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = ChunkContextMemory.objects.filter(is_deleted=False, novel__is_deleted=False)
        if hasattr(user, 'roles') and user.roles.filter(name='admin').exists():
            return qs
        return qs.filter(novel__user=user) 