from rest_framework import viewsets, permissions
from oauth.models.user import User
from oauth.serializers.user import UserSerializer
from oauth.views.role import IsAdmin
 
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin] 