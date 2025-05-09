from rest_framework import viewsets, permissions
from oauth.models.role import Role
from oauth.serializers.user import RoleSerializer

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.roles.filter(name='admin').exists()

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin] 