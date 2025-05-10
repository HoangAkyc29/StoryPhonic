from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    - User chỉ thao tác object của mình.
    - Admin (role 'admin') thao tác mọi object.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        # Nếu user có role admin thì cho phép tất cả
        if hasattr(user, 'roles') and user.roles.filter(name='admin').exists():
            return True
        # Nếu object có trường user (owner)
        if hasattr(obj, 'user'):
            return obj.user == user
        # Nếu object liên kết với novel
        if hasattr(obj, 'novel') and hasattr(obj.novel, 'user'):
            return obj.novel.user == user
        return False 