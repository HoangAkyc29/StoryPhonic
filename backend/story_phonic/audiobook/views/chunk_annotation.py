from rest_framework import viewsets, permissions
from ..models.chunk_annotation import ChunkAnnotation
from ..serializers.chunk_annotation import ChunkAnnotationSerializer
from ..permissions import IsOwnerOrAdmin

class ChunkAnnotationViewSet(viewsets.ModelViewSet):
    serializer_class = ChunkAnnotationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = ChunkAnnotation.objects.filter(is_deleted=False, novel__is_deleted=False)
        if hasattr(user, 'roles') and user.roles.filter(name='admin').exists():
            return qs
        return qs.filter(novel__user=user) 