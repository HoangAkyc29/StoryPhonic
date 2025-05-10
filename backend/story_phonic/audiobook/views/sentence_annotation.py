from rest_framework import viewsets, permissions
from ..models.sentence_annotation import SentenceAnnotation
from ..serializers.sentence_annotation import SentenceAnnotationSerializer
from ..permissions import IsOwnerOrAdmin

class SentenceAnnotationViewSet(viewsets.ModelViewSet):
    serializer_class = SentenceAnnotationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = SentenceAnnotation.objects.filter(is_deleted=False, novel__is_deleted=False)
        if hasattr(user, 'roles') and user.roles.filter(name='admin').exists():
            return qs
        return qs.filter(novel__user=user) 