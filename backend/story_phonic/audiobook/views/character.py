from rest_framework import viewsets, permissions
from ..models.character import Character
from ..serializers.character import CharacterSerializer
from ..permissions import IsOwnerOrAdmin

class CharacterViewSet(viewsets.ModelViewSet):
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Character.objects.filter(is_deleted=False, novel__is_deleted=False)
        novel_id = self.request.query_params.get('novel_id')
        if novel_id:
            qs = qs.filter(novel_id=novel_id)
        if hasattr(user, 'roles') and user.roles.filter(name='admin').exists():
            return qs
        return qs.filter(novel__user=user) 