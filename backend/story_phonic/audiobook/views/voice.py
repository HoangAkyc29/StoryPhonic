from rest_framework import viewsets, permissions
from ..models.voice import Voice
from ..serializers.voice import VoiceSerializer
from ..permissions import IsOwnerOrAdmin

class VoiceViewSet(viewsets.ModelViewSet):
    serializer_class = VoiceSerializer
    queryset = Voice.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin] 